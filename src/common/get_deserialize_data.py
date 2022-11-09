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

import base64
from src.common.deserialize import object_detection_top, bounding_box, bounding_box_2d


def get_deserialize_data(serialize_data):
    """Get access information from yaml and generate ConsoleAccess client
    Returns:
        ConsoleAccessClient: CosoleAccessClient Class generated from access information.
    """
    buf = {}
    buf_decode = base64.b64decode(serialize_data)
    ppl_out = object_detection_top.ObjectDetectionTop.GetRootAsObjectDetectionTop(buf_decode, 0)
    obj_data = ppl_out.Perception()
    res_num = obj_data.ObjectDetectionListLength()
    for i in range(res_num):
        obj_list = obj_data.ObjectDetectionList(i)
        union_type = obj_list.BoundingBoxType()
        if union_type == bounding_box.BoundingBox.BoundingBox2d:
            bbox_2d = bounding_box_2d.BoundingBox2d()
            bbox_2d.Init(obj_list.BoundingBox().Bytes, obj_list.BoundingBox().Pos)
            buf[str(i + 1)] = {}
            buf[str(i + 1)]['C'] = obj_list.ClassId()
            buf[str(i + 1)]['P'] = obj_list.Score()
            buf[str(i + 1)]['X'] = bbox_2d.Left()
            buf[str(i + 1)]['Y'] = bbox_2d.Top()
            buf[str(i + 1)]['x'] = bbox_2d.Right()
            buf[str(i + 1)]['y'] = bbox_2d.Bottom()

    return buf
