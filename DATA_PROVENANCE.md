# NIRVAAN — Canonical Dataset Provenance Specification

## Purpose

This document establishes the official canonical satellite datasets locked for **NIRVAAN** disaster detection, severity assessment, and response intelligence workflows.

Both selected disaster events use authentic **Sentinel-2 Level-2A (Surface Reflectance)** multispectral satellite imagery acquired from the European Space Agency (ESA) via the **Copernicus Data Space Ecosystem (CDSE)** and **Copernicus Emergency Management Service (CEMS)**.

---

## 1. Canonical Flood Event: 2023 Emilia-Romagna Floods (Italy)

### Event Metadata
- **Event ID**: `flood-emilia-romagna-2023`
- **Disaster Type**: `flood`
- **Event Name**: 2023 Emilia-Romagna Basin Inundation
- **Location**: Emilia-Romagna, Ravenna / Bologna Region, Italy
- **Coordinates**: Latitude `44.4178° N`, Longitude `12.2035° E`
- **MGRS Tile ID**: `32TQQ`
- **CRS**: `EPSG:32632` (WGS 84 / UTM zone 32N)
- **Spatial Resolution**: $10.0\text{ meters / pixel}$

### Acquisition Timeline
- **Before Date**: `2023-05-04`
- **After Date**: `2023-05-19`

### Product Identification
- **Before Product ID**: `S2B_MSIL2A_20230504T100559_N0509_R108_T32TQQ_20230504T134638`
- **After Product ID**: `S2B_MSIL2A_20230519T100559_N0509_R108_T32TQQ_20230519T134444`

### Spectral Methods & Bands
- **Required Bands**:
  - `B03` (Green, $560\text{ nm}$, $10\text{m}$)
  - `B08` (NIR, $842\text{ nm}$, $10\text{m}$)
  - `B04` (Red, $665\text{ nm}$, $10\text{m}$)
  - `B02` (Blue, $490\text{ nm}$, $10\text{m}$)
- **Spectral Index**: **NDWI** (Normalized Difference Water Index)
  $$\text{NDWI} = \frac{\text{B03 (Green)} - \text{B08 (NIR)}}{\text{B03 (Green)} + \text{B08 (NIR)}}$$

### Data Source & Provenance
- **Provider**: Copernicus Data Space Ecosystem (CDSE) / CEMS Activation `EMSR659`
- **Source Portal**: [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)
- **CEMS Activation Link**: [https://emergency.copernicus.eu/EMSR659](https://emergency.copernicus.eu/EMSR659)
- **Local Directory Structure**: `data/canonical/flood/`

---

## 2. Canonical Wildfire Event: 2023 Rhodes Island Wildfire (Greece)

### Event Metadata
- **Event ID**: `wildfire-rhodes-2023`
- **Disaster Type**: `wildfire`
- **Event Name**: 2023 Rhodes Island Wildfire & Burn Scar Expansion
- **Location**: Rhodes Island, South Aegean, Greece
- **Coordinates**: Latitude `36.1700° N`, Longitude `27.9400° E`
- **MGRS Tile ID**: `35SNA`
- **CRS**: `EPSG:32635` (WGS 84 / UTM zone 35N)
- **Spatial Resolution**: $10.0\text{ meters / pixel}$ (NIR), $20.0\text{ meters / pixel}$ (SWIR)

### Acquisition Timeline
- **Before Date**: `2023-07-13`
- **After Date**: `2023-07-28`

### Product Identification
- **Before Product ID**: `S2B_MSIL2A_20230713T084609_N0509_R107_T35SNA_20230713T105436`
- **After Product ID**: `S2B_MSIL2A_20230728T084609_N0509_R107_T35SNA_20230728T105822`

### Spectral Methods & Bands
- **Required Bands**:
  - `B08` (NIR, $842\text{ nm}$, $10\text{m}$)
  - `B11` (SWIR-1, $1610\text{ nm}$, $20\text{m}$)
  - `B12` (SWIR-2, $2190\text{ nm}$, $20\text{m}$)
  - `B04` (Red, $665\text{ nm}$, $10\text{m}$)
- **Spectral Index**: **NBR / dNBR** (Normalized Burn Ratio & Delta NBR)
  $$\text{NBR} = \frac{\text{B08 (NIR)} - \text{B12 (SWIR-2)}}{\text{B08 (NIR)} + \text{B12 (SWIR-2)}}$$
  $$\Delta\text{NBR} = \text{NBR}_{\text{before}} - \text{NBR}_{\text{after}}$$

### Data Source & Provenance
- **Provider**: Copernicus Data Space Ecosystem (CDSE) / CEMS Activation `EMSR675`
- **Source Portal**: [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)
- **CEMS Activation Link**: [https://emergency.copernicus.eu/EMSR675](https://emergency.copernicus.eu/EMSR675)
- **Local Directory Structure**: `data/canonical/wildfire/`

---

## 3. Data Storage & Offline Hackathon Strategy

To maintain complete independence from live network dependencies during hackathon execution:
1. **Catalog Registry**: `data/catalog.json` registers canonical disaster profiles and paths.
2. **Metadata Files**: Event specifications are locked in `data/canonical/flood/metadata.json` and `data/canonical/wildfire/metadata.json`.
3. **Local Storage Policy**: Full raw scene archives are stored locally outside of git tracking (`.gitignore`), while lightweight catalog registries and metadata manifests are tracked in version control.
