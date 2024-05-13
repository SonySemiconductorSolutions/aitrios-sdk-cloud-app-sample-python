"""
Copyright 2023 Sony Semiconductor Solutions Corp. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import base64
import time
import boto3
from src.common import get_client
from src.common.util import get_ocsp_status


def get_image_from_aws(retry_count, device_id, sub_directory, order_by="ASC", skip=0, number_of_images=50):
    """Get the image from AWS
    Args:
        retry_count (int): Number of retries on failure
        device_id (str): Device id
        sub_directory (str): image file uploaded directory
        order_by (str): Sort order by date and time the image was created. DESC, ASC
        skip (int): Number of images to skip fetching
        number_of_images (int): Number of images acquired
    Returns:
        total_image_count (int): get images number
        images :[{
            contents (str): base64 encode image data
            name (str): image file name
        }]
    """
    image_response = {
        "total_image_count": 0,
        "images": []
    }
    access_info = get_client.get_aws_access_settings()
    access_key_id = access_info["access_key_id"]
    secret_access_key = access_info["secret_access_key"]
    region = access_info["region"]

    s3_client = _get_s3_client(access_key_id, secret_access_key, region)

    bucket_name = access_info["bucket_name"]
    prefix = f"{device_id}/image/{sub_directory}/"

    image_name_list = _get_key_list_from_aws(s3_client, bucket_name, prefix)
    if order_by == "DESC":
        image_name_list.sort(reverse=True)

    images = []

    for i in range(skip, skip + number_of_images):
        if i >= len(image_name_list):
            break
        image_name = image_name_list[i].split("/")[3]

        response = s3_client.get_object(Bucket=bucket_name, Key=image_name_list[i])
        contents = response["Body"].read()
        b64encoded = base64.b64encode(contents)

        images.append({
            "name": image_name,
            "contents": b64encoded.decode()
        })

    if len(images) > 0:
        image_response["total_image_count"] = len(image_name_list)
        image_response["images"] = images
        return image_response

    if retry_count > 0:
        time.sleep(1)
        return get_image_from_aws(retry_count - 1,
                                  device_id,
                                  sub_directory,
                                  order_by,
                                  skip,
                                  number_of_images)

    return image_response


def get_inference_from_aws(retry_count,
                           device_id,
                           sub_directory,
                           start_inference_time=None,
                           end_inference_time=None,
                           number_of_inference_result=None):
    """Get inference_data from AWS
    Args:
        retry_count (int): Number of retries on failure
        device_id (str): Device id
        sub_directory (str): image file uploaded directory
        start_inference_time (str): start range.
        end_inference_time (str): end range.
        number_of_inference_result (int): Number of cases to get.
    Returns:
        inferences (arr): inference results
    """
    number_of_inference_result = number_of_inference_result if number_of_inference_result is not None else 20
    inferences = []
    access_info = get_client.get_aws_access_settings()
    access_key_id = access_info["access_key_id"]
    secret_access_key = access_info["secret_access_key"]
    region = access_info["region"]

    s3_client = _get_s3_client(access_key_id, secret_access_key, region)

    bucket_name = access_info["bucket_name"]
    prefix = f"{device_id}/metadata/{sub_directory}/"

    inference_name_list = _get_key_list_from_aws(s3_client, bucket_name, prefix)

    for file_path in inference_name_list:
        timestamp = file_path.split("/")[3].replace(".txt", "")
        if (start_inference_time is None or timestamp >= start_inference_time) and\
                (end_inference_time is None or timestamp < end_inference_time):
            response = s3_client.get_object(Bucket=bucket_name, Key=file_path)

            contents = json.loads(response["Body"].read())
            inferences.append(contents["Inferences"][0]["O"])

        if end_inference_time is not None and timestamp > end_inference_time:
            break

        if len(inferences) >= number_of_inference_result:
            break

    if len(inferences) > 0:
        return inferences

    if retry_count > 0:
        time.sleep(1)
        return get_inference_from_aws(retry_count - 1,
                                      device_id,
                                      sub_directory,
                                      start_inference_time,
                                      end_inference_time,
                                      number_of_inference_result)
    return inferences


def _get_s3_client(access_key_id, secret_access_key, region):
    """Get inference_data from AWS
    Args:
        access_key_id: Required to retrieve Amazon S3 information
        secret_access_key: Required to retrieve Amazon S3 information
        region: Subdirectory Required to retrieve Amazon S3 information
    Returns:
        s3_client (obj): s3_clien information
    """
    s3_client = boto3.client('s3', aws_access_key_id=access_key_id,
                             aws_secret_access_key=secret_access_key,
                             region_name=region)
    endpoint_url = s3_client.meta.endpoint_url
    get_ocsp_status(endpoint_url)

    return s3_client


def _get_key_list_from_aws(s3_client, bucket_name, prefix):
    """Get inference_data from AWS
    Args:
        s3_client: Amazon S3 client information
        bucket_name : Bucket name registered in S3
        prefix: Subdirectory path stored in the bucket
    Returns:
        inferences (arr): inference results
    """
    key_name_list = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=1000, Delimiter='/')
    if response.get('Contents') is None:
        return key_name_list
    for obj in response.get('Contents'):
        key_name_list.append(obj["Key"])

    while response.get('IsTruncated') is True:
        marker = response.get('Contents')[-1]['Key']
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=1000, StartAfter=marker, Delimiter='/')
        for obj in response.get('Contents'):
            key_name_list.append(obj["Key"])
    return key_name_list
