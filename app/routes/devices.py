###############################################################################
#  devices.py for archivist descry microservices                              #
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
"""Routes to interact with scanning devices."""
# }}}

# libraries # {{{
import base64
from io import BytesIO
from flask import Blueprint, request
from app.utils import desanity, DesanityUnknownDev, DesanityException
from app.utils import DesanityDeviceBusy
# }}}

devices_bp = Blueprint('devices', __name__)


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
    # try to get the devices throw a internal server error if it fails
    try:
        devices = list(map(lambda dev: {
            'name': dev.name,
            'guid': dev.guid
        }, desanity.devices))
    except DesanityException as ex:
        return {
            'ErrMsg': f"An error occured while getting devices: {ex}"
        }, 500

    # return the devices returned by desanity
    return {
        'devices': devices
    }, 200


@devices_bp.route('/<string:guid>', methods=['GET'])
def get_device(guid):
    """
    Get list of open devices.

    ---
    tags:
      - devices
    responses:
      200:
        description: List of devices
      500:
        description: Internal Error
    """
    try:
        dev = get_device_by_guid(guid)
        print('got dev?')
        return dev.serialize_json(), 200
    except StopIteration:
        return {
            'ErrorMsg': f'Unabled to find resource {guid}'
        }, 404
    except DesanityException as ex:
        return {
            'ErrorMsg': f"Internal Server Error {ex}"
        }, 500


@devices_bp.route('/<string:guid>/enable', methods=['PUT'])
def open_device(guid):
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
      404:
         description: Device not found
    """
    try:
        dev = get_device_by_guid(guid)
        dev.enable()
    except StopIteration:
        return {
            'ErrMsg': f'Sane device {guid} not found'
        }, 404
    except DesanityException as ex:
        return {
            'ErrMsg': f'Internal Server Error {str(ex)}'
        }, 500

    return {
        'device': guid,
        'status': 'enabled'
    }, 201


@devices_bp.route('/<string:guid>/disable', methods=['PUT'])
def close_device(guid):
    """
    Close a SANE device within Descry.

    ---
    tags:
      - devices
    """
    try:
        dev = get_device_by_guid(guid)
        dev.disable()
    except StopIteration:
        return {
            'ErrMsg': f'Sane device {guid} not found'
        }, 404
    except DesanityUnknownDev as ex:
        return {
            'ErrMsg': f'Internal Server Error {str(ex)}'
        }, 500

    return {
        'device': guid,
        'status': 'disabled'
    }


@devices_bp.route('/<string:guid>/options', methods=['GET'])
def get_device_option(guid):
    """
    Get a scanning device option.

    ---
    parameters:
      - name: device_name
        id: path
        description: option of a device
        required: True
        type: string
    response:
      200:
        description: the option information
    """
    try:
        dev = get_device_by_guid(guid)
        return {
            'device': guid,
            'options': dev.options
        }, 200
    except StopIteration:
        return {
            'ErrMsg': f'Sane device {guid} not found'
        }, 404


@devices_bp.route('/<string:guid>/options', methods=['PUT'])
def set_device_option(guid):
    """
    Set a scanning device option.

    ---
    parameters:
      - name: device_name
        id: path
        description: option of a device
        required: True
        type: string
    response:
      200:
        description: the option information
    """
    try:
        dev = get_device_by_guid(guid)
        req = request.args

        if req is None or 'option' not in req or 'value' not in req:
            return {
                'ErrMsg': 'Invalid request'
            }, 400

        opt = req['option']
        value = req['value']

        dev.set_option(opt, value)
        return {
            'status': 'updated'
        }, 200
    except StopIteration:
        return {
            'ErrMsg': f'Sane device {guid} not found'
        }, 404
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Unknown scanner device {guid}'
        }, 500


@devices_bp.route('/<string:guid>/scan', methods=['GET'])
def scan(guid):
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
      202:
        description: Return the job resource handler for the scanning job
      404:
        description: Device not found
      503:
        description: Device is busy
    """
    try:
        dev = get_device_by_guid(guid)
        job = dev.scan()
    except StopIteration:
        return {
            'ErrMsg': f'Sane device {guid} not found'
        }, 404
    except DesanityDeviceBusy:
        return {
            "ErrMsg": f"Sane device {guid} is busy"
        }, 503

    return {
        'jobId': job.job_number,
        'job_url': job_url(guid, job.job_number)
    }, 202


@devices_bp.route('/<string:guid>/jobs', methods=['GET'])
def get_job(guid):
    """
    """
    try:
        dev = get_device_by_guid(guid)
        return {
            'jobs': list(map(lambda job: job.guid, dev.jobs))
        }, 200
    except:
        return {
            'fuck': 'holy shit'
        }, 500


def image2base64str(image, fmt="JPEG"):
    """Return a base64 string of an PIL Image."""
    buf = BytesIO()
    image.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def job_url(device_name, job_number):
    """Return a job url."""
    return f"{request.url_root}devices/{device_name}/jobs/{job_number}"


def get_device_by_guid(guid):
    """Return a DesanityDevice by guid."""
    return next(dev for dev in desanity.devices if dev.guid == guid)
