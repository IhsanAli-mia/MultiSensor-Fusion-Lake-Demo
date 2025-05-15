import os
from minio import Minio
from pathlib import Path
import zarr
import numpy as np
from PIL import Image
import xarray as xr
import tifffile

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

def main():
    # MinIO server configuration
    minio_client = Minio(
        "localhost:9000",  
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False 
    )

    # Source directory containing files and .zarr directories
    source_path = Path("../Data_Lake/Test/38-Cloud_test/Natural_False_Color/")
    bucket_name = "fusion-lake"

    # Ensure bucket exists
    if not minio_client.bucket_exists(bucket_name):
        print(f"Creating bucket: {bucket_name}")
        minio_client.make_bucket(bucket_name)

    # Upload regular files and convert to zarr
    for file_path in source_path.glob("*"):
        if file_path.is_file():
            # Upload original file
            minio_path = 'raw/'+str(file_path.name)
            print(f"Uploading file: {file_path}")
            upload_to_minio(minio_client, bucket_name, str(file_path), minio_path)
            
            # Convert to zarr and upload=)
            if file_path.suffix in ['.tif', '.png', '.jpg', '.jpeg','.TIF']:  
                image = tifffile.imread(file_path)
                zarr_dir = file_path.with_suffix(".zarr")
                zarr_dir_str = str(zarr_dir)  # Convert Path object to string

        # Save the image as a Zarr array locally
                zarr.save(zarr_dir_str, image, chunks=np.array((512,512)))
        # Create a Zarr array
                # zarr.save(zarr_dir, image, chunks=np.array((512,512)))
            #     zarr_dir = file_path.with_suffix(".zarr")
            #     z = zarr.open_group(zarr_dir, mode="w")  # use open_group instead of open
            #     z.create_dataset(
            #         name="data",
            #         data=img,
            #         shape=img.shape,  # required in newer Zarr
            #         chunks=(512, 512),
            #         overwrite=True
            #     )
            #     # Consolidate metadata
            #     zarr.consolidate_metadata(zarr_dir)

            #     # Upload Zarr to MinIO
                minio_zarr_path = f"raw/{file_path.stem}.zarr"
                print(f"Uploading Zarr store to MinIO: {minio_zarr_path}")
                upload_to_minio(minio_client, bucket_name, zarr_dir, minio_zarr_path)

    # # Upload .zarr directories
    # for zarr_path in source_path.glob("*.zarr"):
    #     if zarr_path.is_dir():
    #         minio_path = str(zarr_path.name)
    #         print(f"Uploading zarr directory: {zarr_path}")
    #         upload_to_minio(minio_client, bucket_name, str(zarr_path), minio_path)

if __name__ == "__main__":
    main()