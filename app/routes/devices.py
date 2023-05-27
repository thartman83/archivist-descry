###############################################################################
#  initialize.py for archivist descry microservices                           #
#  Copyright (c) 2023 Tom Hartman (thomas.lees.hartman@gmail.com)             #
#                                                                             #
#  This program is free software; you can redistribute it and/or              #
#  modify it under the terms of the GNU General Public License                #
#  as published by the Free Software Foundation; either version 2             #
#  of the License, or the License, or (at your option) any later              #
#  version.                                                                   #
#                                                                             #
#  This program is distributed in the hope that it will be useful,            #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#  GNU General Public License for more details.                               #
###############################################################################

# Module DocuString ## {{{
"""Routes to configure scanning devices."""
# }}}

# libraries # {{{
import base64
from flask import Blueprint, request
from io import BytesIO
from app.utils import desanity, DesanityUnknownDev, DesanityException
# }}}

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


@devices_bp.route('', methods=['GET'])
def get_devices():
    """
    Retrieve a list of available devices from the sane.

    ---
    tags:
      - devices
    responses:
      200:
        description: A list of devices
      500:
        description: Error occured while getting a list of available devices
    """
    req = None if not request.is_json else request.get_json()
    no_cache = False

    if req is not None and req.has_key('no_cache'):
        no_cache = bool(req['no_cache'])

    # try to get the devices throw a internal server error if it fails
    try:
        if no_cache:
            devices = desanity.available_devices
        else:
            devices = desanity.refresh_devices()

    except DesanityException as ex:
        return {
            'ErrMsg': f"An error occured while getting devices: {ex}"
        }, 500

    # return the devices returned by desanity
    return {
        'devices': devices
    }, 200


@devices_bp.route('/open', methods=['POST'])
def open_device():
    """
    Open a SANE device within Descry.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        in: body
        description: Name of device to open
        required: true
        type: string
    responses:
      201:
         description: Device is opened
      404:
         description: Device not found
    """
    try:
        data = request.get_json()
        device_name = data['device_name']

        device_id = desanity.open_device(device_name)
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404

    return {
        'device_id': device_id
    }, 201


@devices_bp.route('/<string:device_id>', methods=['GET'])
def get_device(device_id):
    """
    Get the current sane device.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        in: path
        description: name of device to get the information from
        required: true
        type: string
    responses:
      200:
        description: Return information about the device
      404:
        description: Device not found
    """
    try:
        device = desanity.available_devices[device_id]
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_id} not found or not open'
        }, 404

    return {
        device
    }, 200


@devices_bp.route('/<string:device_name>/scan', methods=['GET'])
def scan(device_name):
    """
    Scan a document using device_name.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        id: path
        description: id of the device to scan with
        required: true
        type: string
    responses:
      200:
        description: Return the scan document
      404:
        description: Device not found
    """
    try:
        images = desanity.scan(device_name)
        buf = BytesIO()
        images.save(buf, format="TIFF")
        img_str = base64.b64encode(buf.getvalue()).decode('ascii')
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found or not opened'
        }, 404

    return {
        "image": img_str
    }, 200
