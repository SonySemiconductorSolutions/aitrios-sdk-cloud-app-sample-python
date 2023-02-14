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

import json
from flask import Flask, jsonify, render_template, request
from console_access_library import set_logger
from src.common import get_client, get_deserialize_data

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
        if "error_code" in response.keys():
            error_response = {
                "result": "ERROR",
                "message": "get_devices_data failed"
            }
            return jsonify(error_response), 500

        id_list = []
        for device_list in response["devices"]:
            id_list.append(device_list["device_id"])
        device_data = {
            "devices_data": id_list
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
        if "error_code" in response.keys():
            error_response = {
                "result": "ERROR",
                "message": "get_command_parameter_data failed"
            }
            return jsonify(error_response), 500

        mode = ""
        upload_method_IR = ""
        for parameter in response["parameter_list"]:
            for device_id in parameter["device_ids"]:
                if device_id == select_id:
                    if "Mode" in parameter["parameter"]["commands"][0]["parameters"]:
                        mode = parameter["parameter"]["commands"][0]["parameters"]["Mode"]
                    else:
                        mode = "0"
                    if "UploadMethodIR" in parameter["parameter"]["commands"][0]["parameters"]:
                        upload_method_IR = \
                            parameter["parameter"]["commands"][0]["parameters"]["UploadMethodIR"]
                    else:
                        upload_method_IR = "Mqtt"
        command_param = {
            "mode": mode,
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
    """Get the image and inference_data from Console
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
        if device_id == "":
            error_response = {
                "result": "ERROR",
                "message": "Device ID is not specified."
            }
            return jsonify(error_response), 400

        client_obj = get_client.get_console_client()
        image_response = client_obj.insight.get_images(device_id,
                                                       sub_dir,
                                                       number_of_images=1,
                                                       order_by="DESC")
        latest_image_data = "data:image/jpg;base64," + image_response["images"][0]["contents"]
        latest_image_ts = image_response["images"][0]["name"].replace(".jpg", "")

        inference_response = client_obj.insight.get_inference_results(device_id,
                                                                      number_of_inference_results=1,
                                                                      raw=1,
                                                                      time=latest_image_ts)
        latest_inference_data = inference_response[0]["inferences"][0]["O"]

        # deserialize
        deserialize_data = get_deserialize_data.get_deserialize_data(latest_inference_data)

        image_and_inference = {
            "image": latest_image_data,
            "inference_data": deserialize_data
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
        if "error_code" in response.keys():
            console_error_message = response["message"].split("b\'")[1].replace("'", "")
            error_message = json.loads(console_error_message)["message"]
            error_response = {
                "result": "ERROR",
                "message": error_message
            }
            return jsonify(error_response), 500

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
        client_obj = get_client.get_console_client()
        response = client_obj.device_management.stop_upload_inference_result(device_id)
        if "error_code" in response.keys():
            console_error_message = response["message"].split("b\'")[1].replace("'", "")
            error_message = json.loads(console_error_message)["message"]
            error_response = {
                "result": "ERROR",
                "message": error_message
            }
            return jsonify(error_response), 500
        stop_response = {
            "result": response["result"]
        }
        return jsonify(stop_response)

    except Exception as error:
        error_response = {
            "result": "ERROR",
            "message": str(error)
        }
        return jsonify(error_response), 500


if __name__ == "__main__":
    set_logger("INFO")
    app.run(debug=True)
