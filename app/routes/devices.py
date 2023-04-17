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
from flask import Blueprint, request
from app.utils import desanity, DesanityException
# }}}

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


@devices_bp.route('', methods=['GET'])
def get_devices():
    """
    Retrieve a list of devices from the sane.

    ---
    tags:
      - devices
    responses:
      200:
        description: A list of devices
    """
    req = None if not request.is_json else request.get_json()
    no_cache = False

    if req is not None and req.has_key('no_cache'):
        no_cache = bool(req['no_cache'])

    # try to get the devices throw a internal server error if it fails
    try:
        if no_cache:
            devices = desanity.devices
        else:
            devices = desanity.refresh_devices()

    except DesanityException as ex:
        return {
            'Ok': False,
            'ErrMsg': f"An error occured while getting devices: {ex}"
        }, 500

    # return the devices returned by desanity
    return {
        'Ok': True,
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
      200:
         description: Device is opened
    """
    try:
        data = request.get_json()
        device_name = data['device_name']

        desanity.open_device(device_name)
    except DesanityException:
        return {
            'Ok': False,
            'ErrMsg': f'Error opening sane device {device_name}'
        }, 200

    return {
        'Ok': True,
        'device': device_name
    }, 200


@devices_bp.route('/<string:device>', methods=['GET'])
def get_device(device_name):
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
    """
    try:
        device = desanity.device
    except DesanityException:
        return {
            'Ok': False,
            'ErrMsg': 'Error getting current sane device'
        }, 200

    return {
        'Ok': True,
        'device': device
    }, 200
