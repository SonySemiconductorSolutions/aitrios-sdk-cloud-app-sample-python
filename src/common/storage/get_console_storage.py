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

from src.common import get_client


def get_image_from_console(device_id, sub_directory, order_by=None, skip=None, number_of_images=None):
    """Get the image from Console
    Args:
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
    client_obj = get_client.get_console_client()

    image_response = client_obj.insight.get_image_data(device_id=device_id, sub_directory_name=sub_directory, number_of_images=number_of_images, skip=skip, order_by=order_by)

    return image_response


def get_inference_from_console(device_id, start_time=None, end_time=None, number_of_inference_result=None):
    """Get inference_data from Console
    Args:
        device_id (str): Device id
        start_time: Parameters used in filter options.
        end_time: Parameters used in filter options.
        number_of_inference_result: Parameters used in filter options.
    Returns:
        inference_response: inference result
    """
    client_obj = get_client.get_console_client()
    filter = f"EXISTS(SELECT VALUE i FROM i IN c.Inferences WHERE i.T >= \'{start_time}\' AND i.T <= \'{end_time}\')"
    raw = 1
    time = None
    inference_response = client_obj.insight.get_inference_results(device_id, filter, number_of_inference_results=number_of_inference_result, raw=raw, time=time)
    inferences_response = []
    for inference in inference_response:
        inferences_response.append(inference["inference_result"]["Inferences"][0]["O"])
    return inferences_response
