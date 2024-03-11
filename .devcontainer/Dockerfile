# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.11, 3.10, 3.9, 3.8, 3.11-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3-buster, 3.11-buster, 3.10-buster, 3.9-buster, 3.8-buster
ARG VARIANT=3.11-bullseye
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}
RUN apt-get update && apt-get install -y \
    linux-libc-dev \
    libncurses-dev \
    ncurses-base \
    ncurses-bin \
    libsystemd0 \
    libudev1 \
    libunbound8 \
    libpq-dev \
    libx11-6 \
    libx11-data \
    libwebp-dev \
    curl \
    libcurl3-gnutls \
    libkrb5-dev \
    libkdb5-10 \
    libmariadb-dev \
    libssl-dev \
    mariadb-common \
    openssh-client \
    openssl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# [Choice] Node.js version: none, lts/*, 18, 16, 14, 12, 10
ARG NODE_VERSION="18"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

ARG LIBRARY_DIR="/tmp/lib"
ARG CONSOLE_LIB_DIR="${LIBRARY_DIR}/cal"

# Upgrading pip, setuptools
RUN pip install --upgrade pip setuptools

# Install the Console Python Library
COPY .devcontainer/Dependencies/cal ${CONSOLE_LIB_DIR}
RUN pip install ${CONSOLE_LIB_DIR}/lib/python-client
RUN pip install ${CONSOLE_LIB_DIR}/src

