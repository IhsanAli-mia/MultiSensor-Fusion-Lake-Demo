# %%
import s3fs
from datetime import datetime, timedelta
import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.sat import SatExtension
import os
from minio import Minio
import tifffile
from pathlib import Path
import zarr
import numpy as np
import shutil
import re
from dateutil import parser
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
import gdal

# %%
def upload_to_minio(client, bucket_name, local_path, minio_path):
    """Upload a file or directory to MinIO server"""
    if os.path.isfile(local_path):
        client.fput_object(bucket_name, minio_path, local_path)
    elif os.path.isdir(local_path):
        for root, _, files in os.walk(local_path):
            for file in files:
                local_file_path = os.path.join(root, file)
                minio_file_path = os.path.join(minio_path, os.path.relpath(local_file_path, local_path))
                client.fput_object(bucket_name, minio_file_path, local_file_path)
                
minio_client = Minio(
    "localhost:9000",  
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False 
)

# %%
source_path = Path("../Data_Lake/Test/38-Cloud_test/Natural_False_Color/")
bucket_name = "fusion-lake"
metadata_path = Path("./Test/38-Cloud_95-Cloud_Test_Metadata_Files/38-Cloud_95-Cloud_Test_Metadata_Files")

# %%
def parse_mtl(mtl_file):
    """Parses the Landsat MTL file."""
    metadata = {}
    current_group = None

    with open(mtl_file, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith("GROUP ="):
                current_group = line.split("=")[1].strip()
                metadata[current_group] = {}
            elif line.startswith("END_GROUP ="):
                current_group = None
            elif "=" in line and current_group:
                parts = line.split("=")
                key = parts[0].strip()
                value = parts[1].strip().replace('"', '')  # Remove quotes
                metadata[current_group][key] = value
    return metadata

# %%
def reproject_landsat(mtl_file, band_file, output_file):  #ECEF

    """Reprojects a Landsat band to ECEF (EPSG:4978)."""

    mtl_metadata = parse_mtl(mtl_file) #Parse the MTL file
    projection_parameters = mtl_metadata.get("PROJECTION_PARAMETERS", {}) #Access projection parameters

    # 1.  Define source CRS
    # utm_zone = int(projection_parameters.get("UTM_ZONE"))
    # source_crs = CRS.from_epsg(32600 + utm_zone)  # UTM zone is given by EPSG:326xx or 327xx

    # 2.  Define target CRS (ECEF)
    dst_crs = CRS.from_epsg(4978) # ECEF, using its EPSG code

    # 3. Open the raster
    with rasterio.open(band_file) as src:
        transform, width, height = calculate_default_transform(
            src.crs,
            dst_crs,
            src.width,
            src.height,
            *src.bounds
        )

        # 4. Update the metadata
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        # 5. Reproject and write
        with rasterio.open(output_file, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)

# %%
for file_path in source_path.glob("*"):
    if file_path.is_file():
        if file_path.suffix == ".tif" or file_path.suffix == ".TIF":
            image = tifffile.imread(file_path)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]

            mtl_filename = f"{base_name}_MTL.txt"
            
            full_path = os.path.join(metadata_path, mtl_filename)
            # metadata = parse_mtl(full_path)
            
            gdal.Warp('output.tif', file_path, format='GTiff', dstSRS='EPSG:4978')
            
            break


