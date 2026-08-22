"""
NIRVAAN Real Satellite Imagery Ingestion Service (services/satellite_service.py)

Ingests real Sentinel-2 Level-2A satellite observations from the official Copernicus Data Space
Ecosystem (CDSE) STAC API and Open-Meteo Environmental APIs. Stores real scene metadata,
bounding boxes, cloud cover, acquisition timestamps, and STAC asset links into SQLite.
Retrieves real multispectral raster bands (B02, B03, B04, B08, B11, B12) via authenticated
Copernicus Sentinel Hub Process API.
"""

from datetime import datetime, timedelta, timezone
import io
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse
import urllib.request
import urllib.error

import numpy as np
from PIL import Image

from db.repository import DatabaseRepository
from services.copernicus_auth import CopernicusAuthManager, get_copernicus_auth

logger = logging.getLogger("nirvaan.satellite_service")

# Official Copernicus Data Space Ecosystem STAC base URL
DEFAULT_COPERNICUS_STAC_BASE = "https://stac.dataspace.copernicus.eu/v1/"
DEFAULT_COPERNICUS_PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
OPEN_METEO_FLOOD_ENDPOINT = "https://flood-api.open-meteo.com/v1/flood"


class SatelliteIngestionService:
    """
    Service for querying, retrieving, and storing real satellite scenes from official STAC catalog endpoints
    and retrieving real spectral raster bands from Copernicus Data Space.
    """

    def __init__(
        self,
        repo: Optional[DatabaseRepository] = None,
        auth_manager: Optional[CopernicusAuthManager] = None,
        stac_base_url: Optional[str] = None,
        process_url: str = DEFAULT_COPERNICUS_PROCESS_URL,
    ):
        self.repo = repo or DatabaseRepository()
        self.auth_manager = auth_manager or get_copernicus_auth()
        self.stac_base_url = (
            stac_base_url
            or os.getenv("COPERNICUS_STAC_URL")
            or DEFAULT_COPERNICUS_STAC_BASE
        ).rstrip("/") + "/"
        self.stac_search_url = urllib.parse.urljoin(self.stac_base_url, "search")
        self.process_url = process_url

    def create_bbox_from_latlon(self, lat: float, lon: float, delta_deg: float = 0.15) -> List[float]:
        """
        Creates a bounding box [min_lon, min_lat, max_lon, max_lat] centered around target lat/lon.
        """
        min_lon = round(lon - delta_deg, 4)
        max_lon = round(lon + delta_deg, 4)
        min_lat = round(lat - delta_deg, 4)
        max_lat = round(lat + delta_deg, 4)
        return [min_lon, min_lat, max_lon, max_lat]

    def search_sentinel2_stac(
        self,
        lat: float,
        longitude: float,
        days_back: int = 90,
        max_cloud_cover: float = 80.0,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Queries official Copernicus Data Space Ecosystem STAC API for real Sentinel-2 L2A scenes around lat/lon.
        """
        bbox = self.create_bbox_from_latlon(lat, longitude)
        now_dt = datetime.now(timezone.utc)
        start_dt = now_dt - timedelta(days=days_back)
        datetime_range = f"{start_dt.strftime('%Y-%m-%dT00:00:00Z')}/{now_dt.strftime('%Y-%m-%dT23:59:59Z')}"

        payload_dict: Dict[str, Any] = {
            "collections": ["sentinel-2-l2a"],
            "bbox": bbox,
            "datetime": datetime_range,
            "limit": limit
        }

        # Some STAC implementations accept query filter for cloud cover
        if max_cloud_cover < 100.0:
            payload_dict["query"] = {
                "eo:cloud_cover": {"lt": max_cloud_cover}
            }

        payload = json.dumps(payload_dict).encode("utf-8")

        req = urllib.request.Request(
            self.stac_search_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NIRVAAN-Disaster-Intelligence/1.0"
            }
        )

        results = []
        try:
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                features = data.get("features", [])

                for feat in features:
                    scene_id = feat.get("id")
                    props = feat.get("properties", {})
                    acq_time = props.get("datetime") or props.get("created") or now_dt.isoformat()
                    cloud_cov = float(props.get("eo:cloud_cover", 0.0))
                    feat_bbox = feat.get("bbox") or bbox
                    assets = feat.get("assets", {})

                    # Extract primary thumbnail / asset link
                    source_url = (
                        assets.get("thumbnail", {}).get("href")
                        or assets.get("TCI_10m", {}).get("href")
                        or feat.get("links", [{}])[0].get("href", "")
                    )

                    # Extract band URLs (supports Copernicus naming B02_10m or standard b02)
                    def _get_band_href(band_keys: List[str]) -> Optional[str]:
                        for bk in band_keys:
                            if bk in assets:
                                return assets[bk].get("href")
                        return None

                    parsed_meta = {
                        "stac_id": scene_id,
                        "satellite": "Sentinel-2",
                        "sensor": "MSI",
                        "platform": props.get("platform", "Sentinel-2"),
                        "processing_level": props.get("processing:level") or "Level-2A (Surface Reflectance)",
                        "tile_id": props.get("grid:code") or props.get("sentinel:mgrs_tile") or "CDSE-TILE",
                        "cloud_cover": cloud_cov,
                        "acquisition_time": acq_time,
                        "bbox": feat_bbox,
                        "band_urls": {
                            "b02": _get_band_href(["B02_10m", "B02", "blue"]),
                            "b03": _get_band_href(["B03_10m", "B03", "green"]),
                            "b04": _get_band_href(["B04_10m", "B04", "red"]),
                            "b08": _get_band_href(["B08_10m", "B08", "nir"]),
                            "b11": _get_band_href(["B11_20m", "B11", "swir16"]),
                            "b12": _get_band_href(["B12_20m", "B12", "swir22"]),
                            "thumbnail": assets.get("thumbnail", {}).get("href"),
                            "visual": assets.get("TCI_10m", {}).get("href") or assets.get("visual", {}).get("href"),
                        }
                    }

                    # Persist to database
                    saved = self.repo.save_satellite_observation(
                        scene_id=scene_id,
                        provider="Copernicus Data Space Ecosystem (Sentinel-2 L2A)",
                        satellite="Sentinel-2",
                        sensor="MSI",
                        cloud_cover=cloud_cov,
                        acquisition_time=acq_time,
                        bbox=feat_bbox,
                        source_url=source_url,
                        metadata=parsed_meta,
                    )
                    results.append(saved)
        except Exception as e:
            logger.error("Error querying Copernicus STAC API (%s): %s", self.stac_search_url, e)

        return results

    def fetch_sentinel2_bands(
        self,
        bbox: List[float],
        time_from: str,
        time_to: str,
        bands: List[str] = ["B03", "B08"],
        width: int = 64,
        height: int = 64,
        max_cloud_cover: int = 80,
    ) -> Dict[str, np.ndarray]:
        """
        Retrieves real Sentinel-2 Level-2A spectral band arrays from the official Copernicus
        Process API (Sentinel Hub / CDSE) for the specified bounding box and time range.
        Returns a dictionary mapping band name -> float32 NumPy array (values normalized [0.0, 1.0]).
        """
        token = self.auth_manager.get_access_token()
        if not token:
            logger.warning("No Copernicus OAuth2 token available for band retrieval.")
            return {}

        band_arrays: Dict[str, np.ndarray] = {}

        for band in bands:
            band_clean = band.upper().strip()
            evalscript = f"""
//VERSION=3
function setup() {{
  return {{
    input: ["{band_clean}"],
    output: {{ bands: 1, sampleType: "FLOAT32" }}
  }};
}}
function evaluatePixel(sample) {{
  return [sample.{band_clean}];
}}
"""
            payload = {
                "input": {
                    "bounds": {"bbox": bbox},
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": time_from,
                                "to": time_to
                            },
                            "maxCloudCoverage": max_cloud_cover
                        }
                    }]
                },
                "output": {
                    "width": width,
                    "height": height,
                    "responses": [{
                        "identifier": "default",
                        "format": {"type": "image/tiff"}
                    }]
                },
                "evalscript": evalscript
            }

            req = urllib.request.Request(
                self.process_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "NIRVAAN-Disaster-Intelligence/1.0"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=20.0) as resp:
                    if resp.status == 200:
                        raw_tiff = resp.read()
                        img = Image.open(io.BytesIO(raw_tiff))
                        arr = np.array(img, dtype=np.float32)
                        band_arrays[band_clean] = arr
                        logger.info("Successfully fetched Copernicus Sentinel-2 band %s (shape=%s).", band_clean, arr.shape)
            except urllib.error.HTTPError as he:
                if he.code == 401:
                    logger.warning("Copernicus token expired (401). Invalidating cache.")
                    self.auth_manager.invalidate_token()
                logger.warning("Failed to fetch Copernicus band %s: HTTP %d", band_clean, he.code)
            except Exception as e:
                logger.warning("Error fetching Copernicus band %s: %s", band_clean, e)

        return band_arrays

    def fetch_open_meteo_flood_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetches real-time river discharge and hydrological metrics from Open-Meteo Flood API.
        """
        params = urllib.parse.urlencode({
            "latitude": lat,
            "longitude": lon,
            "daily": "river_discharge"
        })
        url = f"{OPEN_METEO_FLOOD_ENDPOINT}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "NIRVAAN-Disaster-Intelligence/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                daily = data.get("daily", {})
                discharges = daily.get("river_discharge", [])
                dates = daily.get("time", [])

                valid_vals = [v for v in discharges if v is not None]
                avg_discharge = float(sum(valid_vals) / len(valid_vals)) if valid_vals else 0.0
                max_discharge = float(max(valid_vals)) if valid_vals else 0.0

                return {
                    "source": "Open-Meteo Global Flood API",
                    "latitude": lat,
                    "longitude": lon,
                    "river_discharge_mean_m3s": round(avg_discharge, 2),
                    "river_discharge_max_m3s": round(max_discharge, 2),
                    "time_series_count": len(discharges),
                    "latest_date": dates[-1] if dates else None
                }
        except Exception as e:
            logger.warning("Error fetching Open-Meteo flood metrics: %s", e)
            return {
                "source": "Open-Meteo Global Flood API",
                "latitude": lat,
                "longitude": lon,
                "error": str(e)
            }


# Default singleton
_DEFAULT_SAT_SERVICE = SatelliteIngestionService()
