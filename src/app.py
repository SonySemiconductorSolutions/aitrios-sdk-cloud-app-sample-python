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

import pytz
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from console_access_library import set_logger
from src.common import get_client, get_deserialize_data, get_storage_data
from src.common.get_client import CONNECTION_DESTINATION, LOCAL_ROOT, Service

app = Flask(__name__)


@app.route("/")
def root():
    """ Displaying html
    """
    return render_template("index.html")


@app.route("/getDeviceData", methods=["GET"])
def get_device_data():
    """Connect to Console and get DeviceData
    Returns:
        Response: List of available devices.
        If get_devices_data is an error create and return an error response
    """
    try:
        client_obj = get_client.get_console_client()
        response = client_obj.device_management.get_devices()
        if "result" in response.keys() and response["result"] in ('ERROR', 'WARNING'):
            error_response = {
                "result": "ERROR",
                "message": "get_devices_data failed"
            }
            return jsonify(error_response), 500

        device_id_list = []
        for device_list in response["devices"]:
            device_id_list.append(device_list["device_id"])
        device_data = {
            "devices_data": device_id_list
        }
        return jsonify(device_data)

    except AttributeError:
        error_response = {
            "result": "ERROR",
            "message": "Unable to create instance."
        }
        return jsonify(error_response), 500
    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response), 500


@app.route("/getCommandParameterFile", methods=["GET"])
def get_command_parameter_file():
    """Get the command_parameter_data in device from Console
    Args:
        device_id (str): Device id
     Returns:
        Response: dict Mode parameter and UploadMethodIR parameter.
        If the ConsoleAccessClient function fails, create and return an error response
    """
    try:
        select_id = request.args.get("device_id")
        if select_id == "":
            error_response = {
                "result": "ERROR",
                "message": "Device ID is not specified."
            }
            return jsonify(error_response), 400

        client_obj = get_client.get_console_client()
        response = client_obj.device_management.get_command_parameter_file()
        if "result" in response.keys() and response["result"] in ('ERROR', 'WARNING'):
            error_response = {
                "result": "ERROR",
                "message": "get_command_parameter_data failed"
            }
            return jsonify(error_response), 500

        mode = 0
        upload_method_IR = "MQTT"
        match_data = [
            parameter for parameter in response["parameter_list"]
            if "device_ids" in parameter
            if select_id in parameter["device_ids"]
        ]
        if len(match_data):
            mode = \
                match_data[0]["parameter"]["commands"][0]["parameters"]["Mode"] \
                if "Mode" in match_data[0]["parameter"]["commands"][0]["parameters"] \
                else 0
            upload_method_IR = \
                match_data[0]["parameter"]["commands"][0]["parameters"]["UploadMethodIR"] \
                if "UploadMethodIR" in match_data[0]["parameter"]["commands"][0]["parameters"] \
                else "MQTT"

        if not ((upload_method_IR == "MQTT" and CONNECTION_DESTINATION == Service.Console) or
                (upload_method_IR == "BlobStorage" and CONNECTION_DESTINATION == Service.Azure) or
                (upload_method_IR == "HTTPStorage" and CONNECTION_DESTINATION == Service.Local)):
            error_response = {
                "result": "ERROR",
                "message": "Command parameters and CONNECTION_DESTINATION do not match."
            }
            return jsonify(error_response), 500

        command_param = {
            "mode": int(mode),
            "upload_methodIR": upload_method_IR
        }
        return jsonify(command_param)
    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response), 500


@app.route("/getImageAndInference", methods=["GET"])
def get_image_and_inference():
    """Get the image and inference_data
    Args:
        device_id (str): Device id
        sub_directory_name (str): image file uploaded directory
     Returns:
        Response: dict containing image data and inference results.
        If the ConsoleAccessClient function fails, create and return an error response
    """
    try:
        device_id = request.args.get("device_id")
        sub_dir = request.args.get("sub_directory_name")
        order_by = "DESC"
        number_of_images = 1
        skip = 0

        if CONNECTION_DESTINATION == Service.Local:
            device_id = ""
            sub_dir = ""

        image_data = get_storage_data.get_image(device_id, sub_dir, order_by, skip, number_of_images)
        if image_data is None or len(image_data.get('images')) == 0:
            error_response = {
                "result": "ERROR",
                "message": "Cannot get images."
            }
            return jsonify(error_response)

        latest_image = image_data["images"][0]
        ts = image_data["images"][0]["name"].replace(".jpg", "")
        base64Img = f"data:image/jpg;base64,{latest_image['contents']}"

        inference = get_storage_data.get_inference(device_id, sub_dir, ts, None, 1)

        if inference is None or len(inference) == 0:
            error_response = {
                "result": "ERROR",
                "message": "Cannot get inference."
            }
            return jsonify(error_response)

        inference_data = get_deserialize_data.get_deserialize_data(inference[0])

        image_and_inference = {
            "image": base64Img,
            "inference_data": inference_data
        }
        return jsonify(image_and_inference)
    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response)


@app.route("/startUpload", methods=["POST"])
def start_upload_inference_result():
    """Specify the device_id, and call the start_upload_inference_result
    Args:
        device_id (str): Device id
     Returns:
        Response: start_upload_inference_result() result.
        if it returns an error, create and return an error response
    """
    try:
        device_id = request.form.get("device_id")
        client_obj = get_client.get_console_client()
        response = client_obj.device_management.start_upload_inference_result(device_id)
        if "result" in response.keys() and response["result"] in ('ERROR', 'WARNING'):
            error_response = {
                "result": "ERROR",
                "message": response["message"]
            }
            return jsonify(error_response), 500

        if CONNECTION_DESTINATION == Service.Local:
            utc_timezone = pytz.utc
            utcDate = datetime.now(utc_timezone)
            outputSubDirectory = utcDate.strftime("%Y%m%d%H%M%S%f")[:-3]
            outputSubDirectoryPath = f"local/deviceId/image/{outputSubDirectory}"
            start_response = {
                "outputSubDirectory": outputSubDirectoryPath,
                "result": response["result"]
            }
        else:
            start_response = {
                "outputSubDirectory": response["outputSubDirectory"],
                "result": response["result"]
            }
        return jsonify(start_response)
    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response), 500


@app.route("/stopUpload", methods=["POST"])
def stop_upload_inference_result():
    """Specify the device_id and call the stop_upload_inference_result
    Args:
        device_id (str): Device id
     Returns:
         Response: stop_upload_inference_result() result.
         if it returns an error, create and return an error response
    """
    try:
        device_id = request.form.get("device_id")
        subDirectory = request.form.get("subDirectory")
        if device_id is None:
            error_response = {
                "result": "ERROR",
                "message": "Unable to obtain Device ID."
            }
            return jsonify(error_response), 500

        if subDirectory is None:
            error_response = {
                "result": "ERROR",
                "message": "Unable to obtain SubDirectory"
            }
            return jsonify(error_response), 500

        if CONNECTION_DESTINATION == Service.Local:
            if not os.path.exists(LOCAL_ROOT):
                error_response = {
                    "result": "ERROR",
                    "message": "Data does not exist"
                }
                return jsonify(error_response), 500

            if not os.path.isabs(LOCAL_ROOT):
                error_response = {
                    "result": "ERROR",
                    "message": "LOCAL_ROOT is only absolute paths are supported."
                }
                return jsonify(error_response), 500

            imageSourceDir = os.path.join(LOCAL_ROOT, "image")
            inferenceSourceDir = os.path.join(LOCAL_ROOT, "meta")

            if not os.path.exists(imageSourceDir) or not os.path.exists(inferenceSourceDir):
                error_response = {
                    "result": "ERROR",
                    "message": "No data in LocalStorage."
                }
                return jsonify(error_response), 500

        client_obj = get_client.get_console_client()
        response = client_obj.device_management.stop_upload_inference_result(device_id)
        if "result" in response.keys() and response["result"] in ('ERROR', 'WARNING'):
            error_response = {
                "result": "ERROR",
                "message": response["message"]
            }
            return jsonify(error_response), 500
        stop_response = {
            "result": response["result"]
        }

        if CONNECTION_DESTINATION == Service.Local:
            imageTargetDir = os.path.join(LOCAL_ROOT, device_id, "image", subDirectory)
            inferenceTargetDir = os.path.join(LOCAL_ROOT, device_id, "meta", subDirectory)

            os.makedirs(imageTargetDir, exist_ok=True)
            os.makedirs(inferenceTargetDir, exist_ok=True)

            imagesFiles = os.listdir(imageSourceDir)
            for fileName in imagesFiles:
                sourceFilePath = os.path.join(imageSourceDir, fileName)
                targetFileDir = os.path.join(imageTargetDir, fileName)
                os.rename(sourceFilePath, targetFileDir)

            inferenceFiles = os.listdir(inferenceSourceDir)
            for fileName in inferenceFiles:
                sourceFilePath = os.path.join(inferenceSourceDir, fileName)
                targetFileDir = os.path.join(inferenceTargetDir, fileName)
                os.rename(sourceFilePath, targetFileDir)

        return jsonify(stop_response)

    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response), 500


if __name__ == "__main__":
    set_logger("INFO")
    if CONNECTION_DESTINATION == Service.Local:
        if not os.path.exists(LOCAL_ROOT):
            raise FileNotFoundError("LOCAL_ROOT is not exists")
        if not os.path.isabs(LOCAL_ROOT):
            raise ValueError("LOCAL_ROOT is only absolute paths are supported.")
    app.run(debug=True)
