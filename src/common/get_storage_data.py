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
from src.common.storage import get_azure_storage, get_console_storage, get_local_storage
from src.common import get_client
from src.common.get_client import CONNECTION_DESTINATION, LOCAL_ROOT, Service
from console_access_library.common.read_console_access_settings import \
    ReadConsoleAccessSettings

RETRY_COUNT = 5


def get_image(device_id, sub_directory, order_by=None, skip=None, number_of_images=None):
    """Get the image from Azure or Console
    Args:
        device_id (str): Device id
        sub_dir (str): image file uploaded directory
        order_by (str): Sort order by date and time the image was created. DESC, ASC
        skip (int): Number of images to skip fetching
        number_of_images (int): Number of images acquired
    Returns:
        result (obj): images data and images file name
    """
    if CONNECTION_DESTINATION == Service.Azure:
        if check_azure_settings("azure_access_settings.yaml"):
            result = get_azure_storage.get_image_from_azure(RETRY_COUNT, device_id, sub_directory, order_by, skip, number_of_images)
    elif CONNECTION_DESTINATION == Service.Local:
        if check_local_settings(LOCAL_ROOT):
            result = get_local_storage.get_image_from_local(RETRY_COUNT, device_id, sub_directory, order_by, skip, number_of_images)
    elif CONNECTION_DESTINATION == Service.Console:
        if check_console_settings("console_access_settings.yaml"):
            result = get_console_storage.get_image_from_console(device_id, sub_directory, order_by, skip, number_of_images)
    return result


def get_inference(device_id, sub_directory, start_inference_time=None, end_inference_time=None, number_of_inference_result=None):
    """Get the inference from Azure or Console or Local
    Args:
        device_id (str): Device id
        sub_dir (str): inference file uploaded directory
        start_inference_time: Option for using filters
        end_inference_time: Option for using filters
        number_of_inference_result: Option for using filters
        timestamp (str): inference file name
    Returns:
        inferences (arr): inferences data
    """
    if CONNECTION_DESTINATION == Service.Azure:
        if check_azure_settings("azure_access_settings.yaml"):
            inferences = get_azure_storage.get_inference_from_azure(RETRY_COUNT, device_id, sub_directory, start_inference_time, end_inference_time, number_of_inference_result)
    elif CONNECTION_DESTINATION == Service.Local:
        if check_local_settings(LOCAL_ROOT):
            inferences = get_local_storage.get_inference_from_local(RETRY_COUNT, device_id, sub_directory, start_inference_time, end_inference_time, number_of_inference_result)
    elif CONNECTION_DESTINATION == Service.Console:
        if check_console_settings("console_access_settings.yaml"):
            inferences = get_console_storage.get_inference_from_console(device_id, start_inference_time, end_inference_time, number_of_inference_result)
    return inferences


def check_azure_settings(settings_path):
    """Check azure settings file
    Args:
        path (str): azure connection settings file path
    Returns:
        True or ValueError
    """
    if not os.path.isfile(os.path.join(os.getcwd(), "src", "common", settings_path)):
        raise ValueError("connection settings file does not exist.")

    connection_info = get_client.get_azure_access_settings()
    if connection_info.get("connection_string") is None or \
            connection_info.get("container_name") is None:
        raise ValueError("Wrong setting. Check the settings.")

    return True


def check_local_settings(local_path):
    """Check local file path
    Args:
        local_path (str): local settings file path
    Returns:
        True or ValueError
    """
    if local_path == "":
        raise ValueError("LOCAL_ROOT is not set.")

    return True


def check_console_settings(settings_path):
    """Check console settings file
    Args:
        path (str): console connection settings file path
    Returns:
        True or ValueError
    """
    setting_file_path = os.path.join(
        os.getcwd(), "src", "common", "console_access_settings.yaml")
    if not os.path.isfile(setting_file_path):
        raise ValueError("connection settings file does not exist.")
    read_console_access_settings_obj = ReadConsoleAccessSettings(
        setting_file_path)
    if read_console_access_settings_obj.console_endpoint is None or \
        read_console_access_settings_obj.portal_authorization_endpoint is None or \
        read_console_access_settings_obj.client_secret is None or \
            read_console_access_settings_obj.client_id is None:
        raise ValueError("Wrong setting. Check the settings.")

    return True
