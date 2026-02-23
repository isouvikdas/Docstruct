import uuid
import os
import tempfile

import boto3
from boto3.s3.transfer import TransferConfig
from django.conf import settings
from .models import Document

bucket_name = settings.AWS_STORAGE_BUCKET_NAME
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

def upload_file(file_obj, file_name: str, file_size: int):
    config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=5
    )

    name, ext = os.path.splitext(file_name)

    key = f"{name}_{uuid.uuid4()}{ext}"

    s3.upload_fileobj(
        Fileobj=file_obj,
        Bucket=bucket_name,
        Key=key,
        Config=config
    )

    file_url = f"https://{bucket_name}.s3.ap-southeast-2.amazonaws.com/{key}"
    return Document(
        file_key=key,
        original_filename=file_name,
        file_size=file_size,
        file_url=file_url
    )


def download_image(key: str):
    response = s3.get_object(Bucket=bucket_name, Key = key)
    return response["Body"].read()

def download_pdf(key: str):
    suffix = os.path.splitext(key)[1]

    tmp_dir = tempfile.gettempdir()
    local_path = os.path.join(tmp_dir, f"{uuid.uuid4()}{suffix}")

    s3.download_file(bucket_name, key, local_path)

    return local_path


