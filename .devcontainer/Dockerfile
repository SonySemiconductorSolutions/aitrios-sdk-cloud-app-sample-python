# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}
RUN apt-get update && apt-get install -y \
    libksba8 \
    linux-libc-dev \
    libexpat1 \
    libexpat1-dev \
    libxml2 \
    libxml2-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="16"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

ARG LIBRARY_DIR="/tmp/lib"
ARG CONSOLE_LIB_DIR="${LIBRARY_DIR}/aitrios-sdk-console-access-lib-python"

# Upgrading pip, setuptools
RUN pip install --upgrade pip setuptools

# Install the Console Python Library
COPY .devcontainer/Dependencies/aitrios-sdk-console-access-lib-python ${CONSOLE_LIB_DIR}
RUN pip install ${CONSOLE_LIB_DIR}/lib/python-client
RUN pip install ${CONSOLE_LIB_DIR}/src

