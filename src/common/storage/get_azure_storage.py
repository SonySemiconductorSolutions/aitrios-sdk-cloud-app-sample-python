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

import base64
import time
import os
from azure.storage.blob import BlobServiceClient
from src.common import get_client
from src.third_party.ocsp_checker import ocspchecker
import json


def get_https_proxy():
    """
    Get proxy setting from environment variable

    Returns:
        - "__proxy_str__" - Proxy string
    """

    proxy_env_var = "https_proxy"
    return os.environ.get(proxy_env_var) or os.environ.get(proxy_env_var.upper())


def get_ocsp_status(host_url):
    """Get OCSP status for the host_url"""
    result = ocspchecker.get_ocsp_status(host=host_url, proxy=get_https_proxy())
    if result[2] != "OCSP Status: GOOD":
        raise Exception("OCSP status not good.")


def get_image_from_azure(retry_count, device_id, sub_directory, order_by="ASC", skip=0, number_of_images=50):
    """Get the image from Azure
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
    access_info = get_client.get_azure_access_settings()
    blob_service_client = BlobServiceClient.from_connection_string(
        access_info["connection_string"])
    get_ocsp_status(blob_service_client.url)
    container_client = blob_service_client.get_container_client(
        access_info["container_name"])

    storage_path = f"{device_id}/image/{sub_directory}"
    blobs_list = container_client.list_blobs(storage_path)
    blob_name_array = []
    for blob in blobs_list:
        blob_name_array.append(blob.name)
    if order_by == "DESC":
        blob_name_array.sort(reverse=True)

    images = []

    for i in range(skip, skip + number_of_images):
        if i >= len(blob_name_array):
            break
        blob_client = container_client.get_blob_client(blob_name_array[i])
        image = blob_client.download_blob()
        image_text = image.read()
        b64encoded = base64.b64encode(image_text)

        file_name = blob_name_array[i].rsplit("/", 1)[1]
        images.append({
            "name": file_name,
            "contents": b64encoded.decode()
        })

    if len(blob_name_array) != 0:
        image_response["total_image_count"] = len(blob_name_array)
        image_response["images"] = images
        return image_response

    if retry_count > 0:
        time.sleep(1)
        return get_image_from_azure(retry_count - 1,
                                    device_id,
                                    sub_directory,
                                    order_by,
                                    skip,
                                    number_of_images)

    return image_response


def get_inference_from_azure(retry_count,
                             device_id,
                             sub_directory,
                             start_inference_time=None,
                             end_inference_time=None,
                             number_of_inference_result=None):
    """Get inference_data from Azure
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
    inferences = []
    access_info = get_client.get_azure_access_settings()
    blob_service_client = BlobServiceClient.from_connection_string(access_info["connection_string"])
    get_ocsp_status(blob_service_client.url)
    container_client = blob_service_client.get_container_client(access_info["container_name"])
    storage_path = f'{device_id}/metadata/{sub_directory}'
    blobs = []

    for blob in container_client.list_blobs(storage_path):
        timestamp = blob.name.split("/")[3].replace(".txt", "")
        if (start_inference_time is None or timestamp >= start_inference_time) and\
                (end_inference_time is None or timestamp < end_inference_time):
            blobs.append(blob.name)
        if end_inference_time is not None and timestamp > end_inference_time:
            break

        if len(blobs) == number_of_inference_result:
            break

    if len(blobs) != 0:
        for blob_name in blobs:
            blob_client = container_client.get_blob_client(blob_name)
            inference = blob_client.download_blob(encoding="UTF-8")
            inference_text = inference.readall()
            inference_obj = json.loads(inference_text)
            inferences.append(inference_obj["Inferences"][0]["O"])
        return inferences

    if retry_count > 0:
        time.sleep(1)
        return get_inference_from_azure(retry_count - 1,
                                        device_id,
                                        sub_directory,
                                        start_inference_time,
                                        end_inference_time,
                                        number_of_inference_result)
    return inferences
