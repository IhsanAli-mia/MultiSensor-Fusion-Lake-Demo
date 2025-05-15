# MultiSensor Fusion Lake Demo

This demo demonstrates a simplified data ingestion and transformation pipeline for a MultiSensor Fusion Data Lake. It uses a local MinIO server to simulate object storage and processes Landsat 8 imagery by reprojecting it into Earth-Centered, Earth-Fixed (ECEF) coordinates. The goal is to standardize spatial data for effective multisensor fusion.

fusion-lake/
├── data/                ← never committed; mounted by workflow
│   ├── raw/             ← S3 prefix  “raw/” (object store truth, chunked Zarr)   ☑
│   ├── posterior/       ← S3 prefix  “posterior/” (µ, Σ, ELBO etc.)              ◻
│   └── scratch/         ← temp workspace, auto-GC’d by Make targets             ◻
├── stac/                ← STAC Items & Collections (JSON)                       ☑
├── src/
│   ├── fusion_lake/     ← importable Python package
│   │   ├── ingest/      ← Stage-1/2 DAG nodes (warp → zarr)                     ☑ (partial)
│   │   ├── posterior/   ← Stage-3 notebooks / Papermill drivers                 ◻
│   │   ├── ledger/      ← Stage-4 append-only Γ log helpers                     ◻
│   │   └── utils/       ← checksum, logging, S3 helpers                         ◻
│   └── __init__.py
├── workflows/
│   ├── ingestion_dag.py  (Prefect)                                              ☑ (partial)
│   └── posterior_dag.py  (Papermill → Zarr)                                     ◻
├── .github/workflows/
│   ├── ci.yml          ← lint + unit + stac-validator                           ◻
│   └── nightly.yml     ← schedule: ‘posterior_dag’ on UTC 00:30                 ◻
├── pyproject.toml      ← poetry + isort + black; pins rasterio ≥1.3, zarr ≥2.17 ☑
├── Makefile            ← `make ingest file=...`  /  `make validate`             ◻
├── README.md           ← usage, DAG diagram, bucket policy snips                ☑
└── LICENSE             ← MIT (client OK’d)                                      ☑

<!-- ## Overview

Data Source: Landsat 8 (32-bit) imagery

Processing Pipeline:

    Parse Landsat MTL (metadata) files

    Reproject GeoTIFF images to EPSG:4978 (ECEF)

    Upload the processed assets to a local MinIO-based data lake

Object Storage: MinIO (S3-compatible)

## Features

    Reprojects satellite imagery to a global coordinate reference system (ECEF)

    Supports ingestion of both single files and directories

    Uploads processed data to an object store using S3-compatible APIs

    Uses STAC metadata and integrates with Zarr format

## Requirements

Python 3.7+

Required packages (install via pip install -r requirements.txt):
```
s3fs
rasterio
numpy
tifffile
zarr
pystac
python-dateutil
minio
GDAL
```
## Usage

    Start Local MinIO Server

    Ensure MinIO is running locally:
```
minio server /data
```
Use the following credentials (as in the script):

    Access Key: minioadmin

    Secret Key: minioadmin

Prepare Data

    Place Landsat .TIF images in: ../Data_Lake/Test/38-Cloud_test/Natural_False_Color/

    Place corresponding MTL metadata files in: ./Test/38-Cloud_95-Cloud_Test_Metadata_Files/

Run Script **stage.ipynb**

The main script:

    Parses MTL metadata

    Reprojects the image to ECEF (EPSG:4978)

    Converts it into a zarr compressed array

    Creates a corresponding STAC Metadata file

    Uploads the zarr array and the STAC file to the fusion-lake bucket in MinIO
 -->

