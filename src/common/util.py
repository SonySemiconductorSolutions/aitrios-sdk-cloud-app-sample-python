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
from pathlib import Path
from src.third_party.ocsp_checker import ocspchecker


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


def file_absolute_path_check(file_path):
    """Check if file path is absolute"""
    if not os.path.isabs(file_path):
        raise ValueError("Only absolute paths are supported.")


def file_symbolic_check(file_path):
    """Check if file path is a symbolic link"""
    if Path(file_path).is_symlink() is True:
        raise IsADirectoryError("Can't open symbolic link file.")


def storage_dir_existence_check(file_path):
    """Check if storage file path exists"""
    if not os.path.exists(file_path):
        raise ValueError("Data does not exist")


def file_existence_check(file_path):
    """Check if setting file path exists"""
    if not os.path.isfile(file_path):
        raise ValueError("connection settings file does not exist.")
