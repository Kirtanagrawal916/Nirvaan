"""
NIRVAAN Real Satellite Imagery Ingestion Service (services/satellite_service.py)

Ingests real satellite observations from Element84 AWS Earth Search STAC API (Sentinel-2 L2A)
and Open-Meteo Environmental APIs. Stores real scene metadata, bounding boxes, cloud cover,
acquisition timestamps, and STAC links into the persistent SQLite database.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse
import urllib.request

from db.repository import DatabaseRepository

logger = logging.getLogger("nirvaan.satellite_service")

STAC_ENDPOINT = "https://earth-search.aws.element84.com/v1/search"
OPEN_METEO_FLOOD_ENDPOINT = "https://flood-api.open-meteo.com/v1/flood"


class SatelliteIngestionService:
    """
    Service for querying, retrieving, and storing real satellite scenes from official STAC catalog endpoints.
    """

    def __init__(self, repo: Optional[DatabaseRepository] = None):
        self.repo = repo or DatabaseRepository()

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
        Queries Element84 Earth Search STAC API for real Sentinel-2 L2A scenes around lat/lon.
        """
        bbox = self.create_bbox_from_latlon(lat, longitude)
        now_dt = datetime.now(timezone.utc)
        start_dt = now_dt - timedelta(days=days_back)
        datetime_range = f"{start_dt.strftime('%Y-%m-%dT00:00:00Z')}/{now_dt.strftime('%Y-%m-%dT23:59:59Z')}"

        payload = json.dumps({
            "collections": ["sentinel-2-l2a"],
            "bbox": bbox,
            "datetime": datetime_range,
            "query": {
                "eo:cloud_cover": {"lt": max_cloud_cover}
            },
            "limit": limit
        }).encode("utf-8")

        req = urllib.request.Request(
            STAC_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NIRVAAN-Disaster-Intelligence/1.0"
            }
        )

        results = []
        try:
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                features = data.get("features", [])

                for feat in features:
                    scene_id = feat.get("id")
                    props = feat.get("properties", {})
                    acq_time = props.get("datetime") or props.get("created") or now_dt.isoformat()
                    cloud_cov = float(props.get("eo:cloud_cover", 0.0))
                    feat_bbox = feat.get("bbox") or bbox
                    assets = feat.get("assets", {})
                    source_url = assets.get("thumbnail", {}).get("href") or feat.get("links", [{}])[0].get("href", "")

                    parsed_meta = {
                        "stac_id": scene_id,
                        "satellite": "Sentinel-2",
                        "sensor": "MSI",
                        "platform": props.get("platform", "Sentinel-2"),
                        "processing_level": "Level-2A (Surface Reflectance)",
                        "tile_id": props.get("grid:code") or props.get("sentinel:mgrs_tile") or "STAC-TILE",
                        "cloud_cover": cloud_cov,
                        "acquisition_time": acq_time,
                        "bbox": feat_bbox,
                        "band_urls": {
                            "green": assets.get("green", {}).get("href"),
                            "nir": assets.get("nir", {}).get("href"),
                            "red": assets.get("red", {}).get("href"),
                            "blue": assets.get("blue", {}).get("href"),
                            "swir16": assets.get("swir16", {}).get("href"),
                            "thumbnail": assets.get("thumbnail", {}).get("href"),
                        }
                    }

                    # Persist to database
                    saved = self.repo.save_satellite_observation(
                        scene_id=scene_id,
                        provider="Element84 AWS / Copernicus Sentinel-2 STAC",
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
            logger.error("Error querying Element84 STAC API: %s", e)

        return results

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
