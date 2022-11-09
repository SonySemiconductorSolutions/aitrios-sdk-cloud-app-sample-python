/*
 * Copyright 2022 Sony Semiconductor Solutions Corp. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

let interval

// eslint-disable-next-line no-unused-vars
function getDeviceData () {
  fetch('/getDeviceData')
    .then((res) => {
      if (!res.ok) {
        throw res
      } else {
        return (res.json())
      }
    })
    .then((json) => {
      const deviceIdList = json.devices_data
      if (json.devices_data.length === 0) {
        return window.alert('Connected device not found.')
      }
      const deviceElm = document.getElementById('device-id-list')
      for (const elem of deviceIdList) {
        const option = document.createElement('option')
        option.value = elem
        option.textContent = elem
        deviceElm.appendChild(option)
      }
    })
    .catch((err) => {
      handleResponseErr(err)
    })
}

// eslint-disable-next-line no-unused-vars
function handleOnChangeDeviceId () {
  const hiddenElements = Array.from(document.querySelectorAll('.hidden'))
  hiddenElements.forEach(element => {
    element.classList.remove('hidden')
  })
}

// eslint-disable-next-line no-unused-vars
function handleOnClickStartBtn () {
  const id = document.getElementById('device-id-list').value
  const startBtn = document.getElementById('start-btn')
  const stopBtn = document.getElementById('stop-btn')

  buttonDisable(startBtn)

  const params = new URLSearchParams()
  params.set('device_id', id)
  
  fetch('/getCommandParameterFile?' + params.toString())
  .then((res) => {
    if (!res.ok) {
      throw res
    } else {
      return (res.json())
    }
  })
  .then((json) => {
    if (json.result === 'ERROR') {
      window.alert(json.message)
      return
    }

    if (!json.mode || !json.upload_methodIR) {
      buttonEnable(startBtn)
      return window.alert('Command parm not found.')
    } else if (json.mode != "1"){
      buttonEnable(startBtn)
      return window.alert('Set CommandParameter Mode to 1(Input Image & Inference Result).')
    } else if (json.upload_methodIR.toUpperCase() != "MQTT"){
      buttonEnable(startBtn)
      return window.alert('Set CommandParameter UploadMethodIR to "Mqtt".')
    }

    const fetchFormEncodedRequest = {
      method: 'POST',
      body: new URLSearchParams({
        device_id: id
      })
    }
    fetch('/startUpload', fetchFormEncodedRequest)
      .then((res) => {
        if (!res.ok) {
          throw res
        } else {
          return (res.json())
        }
      })
      .then((json) => {
        if (json.result === 'ERROR') {
          buttonEnable(startBtn)
          window.alert(json.message)
          return
        }
  
        buttonEnable(stopBtn)
  
        const subDirectoryPathList = json.outputSubDirectory.split('/')
        const subDirectory = subDirectoryPathList[subDirectoryPathList.length - 1]
        params.set('sub_directory_name', subDirectory)
        
        let labelData
        fetch('static/js/label.json')
          .then(res => {
            return (res.json())
          })
          .then((jsondata) => {
            labelData = jsondata
            interval = setInterval(function () { getImageAndInference(params, labelData) }, 5000)
          })
      })
      .catch((err) => {
        buttonEnable(startBtn)
        handleResponseErr(err)
      })

  })
  .catch((err) => {
    buttonEnable(startBtn)
    handleResponseErr(err)
  })

}

function getImageAndInference (params, labeldata) {
  fetch('/getImageAndInference?' + params.toString())
    .then((res) => {
      if (!res.ok) {
        throw res
      } else {
        return (res.json())
      }
    })
    .then((json) => {
      if (json.result === 'ERROR') {
        window.alert(json.message)
        return
      }
      if (Object.keys(json).length === 0) {
        return console.log('Waiting for image upload.')
      }
      drawBoundingBox(json.image, json.inference_data, labeldata)
    })
    .catch((err) => {
      handleResponseErr(err)
    })
}

function drawBoundingBox (image, inferenceData, labeldata) {
  const img = new window.Image()
  img.src = image
  img.onload = () => {
    const canvas = document.getElementById('canvas')
    const canvasContext = canvas.getContext('2d')
    canvas.width = img.width
    canvas.height = img.height
    canvasContext.drawImage(img, 0, 0)
    
    for (const [key, value] of Object.entries(inferenceData)) {
      if (key === 'T') {
        continue
      }
      canvasContext.lineWidth = 3
      canvasContext.strokeStyle = 'rgb(255, 255, 0)'
      canvasContext.strokeRect(value.X, value.Y, Math.abs(value.X - value.x), Math.abs(value.y - value.Y))
      canvasContext.font = '20px Arial'
      canvasContext.fillStyle = 'rgba(255, 255, 0)'
      const labelPointX = (value.x > 270 ? value.x - 70 : value.x)
      const labelPointY = (value.y > 300 ? value.y - 10 : value.y)
      canvasContext.fillText(labeldata[value.C] + ' ' + Math.round((value.P) * 100) + '%', labelPointX, labelPointY)
    }
    
  }
}

// eslint-disable-next-line no-unused-vars
function handleOnClickStopBtn () {
  clearInterval(interval)
  const id = document.getElementById('device-id-list').value
  const startBtn = document.getElementById('start-btn')
  const stopBtn = document.getElementById('stop-btn')
  
  buttonDisable(stopBtn)
  const fetchFormEncodedRequest = {
    method: 'POST',
    body: new URLSearchParams({
      device_id: id
    })
  }
  fetch('/stopUpload', fetchFormEncodedRequest)
    .then((res) => {
      if (!res.ok) {
        throw res
      } else {
        return (res.json())
      }
    })
    .then((json) => {
      if (json.result === 'ERROR') {
        window.alert(json.message)
        buttonEnable(stopBtn)
        return
      }

      buttonEnable(startBtn)

    })
    .catch((err) => {
      buttonEnable(stopBtn)
      handleResponseErr(err)
    })

}

function handleResponseErr (err) {
  if (err.message === 'Failed to fetch') {
    window.alert('Communication with server failed.')
  } else {
    err.json()
      .then(res => {
        window.alert(res.message)
      })
  }
}

function buttonEnable(button){
  button.disabled = false
  button.classList.add('button')
  button.classList.remove('disableButton')
}

function buttonDisable(button){
  button.disabled = true
  button.classList.add('disableButton')
  button.classList.remove('button')
}