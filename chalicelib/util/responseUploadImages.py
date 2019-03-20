import hashlib
import base64
import re
import os
import boto3

s3_client = boto3.client('s3', "us-east-1")
S3_UPLOADS_BUCKET_NAME = os.environ["S3_UPLOADS_BUCKET_NAME"]


def upload_image_to_s3(image):
    if image.startswith("data:"):
        content_type = re.findall("^data:([^;]+);", image)[0]
        content = re.sub("^.*?base64,", "", image)
        name = hashlib.md5(image.encode('utf-8')).hexdigest()
        s3_client.put_object(
            Bucket=S3_UPLOADS_BUCKET_NAME,
            Body=base64.b64decode(content),
            Key=name,
            ContentType=content_type,
            ContentEncoding='base64'
        )
        return name

def process_response_data_images(response_data):
    if "images" in response_data:
        for i, image in enumerate(response_data["images"]):
            response_data["images"][i] = upload_image_to_s3(image)
    # if "image" in response_data:
    #     response_data["image"] = upload_image_to_s3(image)
    return response_data