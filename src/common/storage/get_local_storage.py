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

import os
import base64
import json
import time
from pathlib import Path
from src.common import get_client


def get_image_from_local(retry_count, device_id, sub_directory, order_by="ASC", skip=0, number_of_images=50):
    """Get the image from Local
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
    storage_path = os.path.join(get_client.LOCAL_ROOT, device_id, "image", sub_directory)
    order_by = order_by.upper() if order_by else "ASC"
    images = []
    if not os.path.exists(storage_path):
        raise FileNotFoundError("Data does not exist")

    if not os.path.isabs(storage_path):
        raise ValueError("Only absolute paths are supported.")

    files = os.listdir(storage_path)
    image_files = []
    for file in files:
        if file.lower().endswith(".jpg"):
            image_files.append(file)

    if order_by == "DESC":
        image_files.reverse()

    for i, image_file in enumerate(image_files[skip:]):
        if i == number_of_images:
            break

        file_path = os.path.join(storage_path, image_file)
        symbolic_link = Path(file_path).is_symlink()
        if symbolic_link is True:
            raise IsADirectoryError("Can't open symbolic link file.")
        with open(file_path, "rb") as file:
            data = file.read()
            base64_image = base64.b64encode(data).decode("utf-8")
            images.append({
                "name": image_file,
                "contents": base64_image
            })

    if len(image_files) != 0:
        image_response["total_image_count"] = len(image_files)
        image_response["images"] = images
        return image_response

    if retry_count > 0:
        time.sleep(1)
        return get_image_from_local(retry_count - 1,
                                    device_id,
                                    sub_directory,
                                    order_by,
                                    skip,
                                    number_of_images)

    return image_response


def get_inference_from_local(retry_count, device_id, sub_directory, start_inference_time=None, end_inference_time=None, number_of_inference_result=20):
    """Get inference_data from Local
    Args:
        retry_count (int): Number of retries on failure
        device_id (str): Device id
        sub_directory (str): image file uploaded directory
        start_inference_time (str): When this value is specified, extract the inference result metadata within the following range.
        end_inference_time (str): When this value is specified, extract the inference result metadata within the following range.
        number_of_inference_result (int): Number of cases to get.
    Returns:
        inferences (arr): inference results
    """
    storage_path = os.path.join(get_client.LOCAL_ROOT, device_id, "meta", sub_directory)
    inference_results = []
    if not os.path.exists(storage_path):
        raise FileNotFoundError("Data does not exist")

    if not os.path.isabs(storage_path):
        raise ValueError("Only absolute paths are supported.")

    inference_files = os.listdir(storage_path)
    for file_name in inference_files:
        timestamp = os.path.splitext(file_name)[0]
        if (start_inference_time is None or timestamp >= start_inference_time) and\
                (end_inference_time is None or timestamp < end_inference_time):
            inference_data_path = os.path.join(storage_path, file_name)
            symbolic_link = Path(inference_data_path).is_symlink()
            if symbolic_link is True:
                raise IsADirectoryError("Can't open symbolic link file.")
            with open(inference_data_path, "r") as file:
                inference_data = json.load(file)
                inference_result = inference_data["Inferences"][0]["O"]
                inference_results.append(inference_result)
        elif end_inference_time is not None and timestamp > end_inference_time:
            break
        if len(inference_results) == number_of_inference_result:
            break

    if len(inference_results) != 0:
        return inference_results

    if retry_count > 0:
        time.sleep(1)
        return get_inference_from_local(retry_count - 1,
                                        device_id,
                                        sub_directory,
                                        start_inference_time,
                                        end_inference_time,
                                        number_of_inference_result)

    return inference_results
