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

from setuptools import find_packages, setup

PACKAGE_NAME = "flask_sample_app"
PACKAGE_VERSION = "0.2.0"
PACKAGE_DESCRIPTION = "flask_sample_app"
AUTHOR_NAME = "Sony Semiconductor Solutions Corporation"
AUTHOR_EMAIL = ""
root_dir = os.getcwd()

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_DESCRIPTION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    classifiers=[
        "License :: Confidential :: Sony Semiconductor Solutions Corporation",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        'flask',
        'flatbuffers==1.11.0',
        f'console-access-library @ file://{root_dir}/.devcontainer/Dependencies/aitrios-sdk-console-access-lib-python/src',
        f'aitrios-console-rest-client-sdk-primitive @ file://{root_dir}/.devcontainer/'
        'Dependencies/aitrios-sdk-console-access-lib-python/lib/python-client'
        ],
    extras_require={
        "develop": [
            'pytest',
            'pytest-mock',
            'pytest-cov',
            'pytest-html',
            'sphinx',
            'pip-licenses'],
    },
    entry_points={
    },
    include_package_data=True,
)
