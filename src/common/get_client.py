"""
Copyright 2022 Sony Semiconductor Solutions Corp. All rights reserved.

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

from console_access_library.client import Client

warnings.filterwarnings("ignore")
sys.path.append(".")


def get_console_client():
    """Get access information from yaml and generate ConsoleAccess client
    Returns:
        ConsoleAccessClient: CosoleAccessClient Class generated from access information.
    """

    setting_file_path = os.path.join(os.getcwd(), "src", "common", "console_access_settings.yaml")
    client_obj = Client(setting_file_path)

    return client_obj
