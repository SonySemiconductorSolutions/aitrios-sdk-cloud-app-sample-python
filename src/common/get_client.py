"""
Copyright 2022, 2023 Sony Semiconductor Solutions Corp. All rights reserved.

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
import sys
import warnings
from pathlib import Path
from enum import Enum, auto
import yaml

from console_access_library.client import Client
from console_access_library.common.config import Config
from console_access_library.common.read_console_access_settings import \
    ReadConsoleAccessSettings

warnings.filterwarnings("ignore")
sys.path.append(".")


class Service(Enum):
    Console = auto()
    Azure = auto()
    Local = auto()


CONNECTION_DESTINATION = Service.Console
LOCAL_ROOT = ""


def get_console_client():
    """Get access information from yaml and generate ConsoleAccess client
    Returns:
        ConsoleAccessClient: ConsoleAccessClient Class generated from access information.
    """

    setting_file_path = os.path.join(
        os.getcwd(), "src", "common", "console_access_settings.yaml")
    read_console_access_settings_obj = ReadConsoleAccessSettings(
        setting_file_path)
    config_obj = Config(
        read_console_access_settings_obj.console_endpoint,
        read_console_access_settings_obj.portal_authorization_endpoint,
        read_console_access_settings_obj.client_id,
        read_console_access_settings_obj.client_secret,
        read_console_access_settings_obj.application_id
    )
    client_obj = Client(config_obj)

    return client_obj


def get_azure_access_settings():
    """Get access information from yaml
    Returns:
        config_obj: azure settings
    """

    setting_file_path = os.path.join(
        os.getcwd(), "src", "common", "azure_access_settings.yaml")
    symbolic_link = Path(setting_file_path).is_symlink()
    if symbolic_link is True:
        raise IsADirectoryError("Can't open symbolic link file.")
    with open(setting_file_path, "r") as yaml_file:
        access_info = yaml.safe_load(yaml_file)
        config_obj = {}
        if access_info["azure_access_settings"] is None:
            raise ValueError("Wrong setting. Check the settings.")
        if access_info["azure_access_settings"].get("connection_string") is not None:
            config_obj["connection_string"] = access_info["azure_access_settings"]["connection_string"]
        if access_info["azure_access_settings"].get("container_name") is not None:
            config_obj["container_name"] = access_info["azure_access_settings"]["container_name"]

    return config_obj
