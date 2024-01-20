5###############################################################################
#  backend.py for archivist descry microservices                              #
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
"""Routes to interact with scanning backends."""
# }}}

# libraries # {{{
from flask import Blueprint, request
from app.utils import desanity, DesanityException
# }}}

backend_bp = Blueprint('backend', __name__)


@backend_bp.route('', methods=['GET'])
def get_backend():
    """Get the decry backend configuration."""
    try:
        return {
            'devices': desanity.devices
        }, 200
    except DesanityException as ex:
        return {
            'ErrorMessage': f'Error getting backend information: {ex}'
        }, 500


@backend_bp.route('/discover_device', methods=['GET'])
def get_devices():
    """Discover available devices to Descry."""
    try:
        devices = desanity.refresh_devices()
        return {
            "devices": list(map(lambda dev: dev.name, devices))
        }, 200
    except DesanityException as ex:
        return {
            'ErrorMessage': f'Error discovering devices: {ex}'
        }, 500


@backend_bp.route('/discover_device', methods=['PUT'])
def configure_device():
    """Configure a new Descry device."""
    try:
        req = None if not request.is_json else request.get_json()
        desanity.add_device_by_url(req['device_name'], req['device_url'],
                                   req['type'])

        return 200
    except KeyError as ex:
        return {
            'ErrorMessage': f'Invalid request: {ex}'
        }, 400
    except IOError as ex:
        return {
            'ErrorMessage': f'System error writing configuration file {ex}'
        }, 500
    except DesanityException as ex:
        return {
            'ErrorMessage': f'Error attempting to add a device {ex}'
        }, 500


@backend_bp.route('/device_configurations', methods=['GET'])
def get_device_configurations():
    """Get device type configurations."""
    try:
        req = None if not request.is_json else request.get_json()
        device_type = req['type']
        config = desanity.get_device_configs(device_type)

        return config, 200
    except IOError:
        return {
            'ErrorMessage': f'Error attempting to get {device_type} config'
        }, 500
    except KeyError:
        return {
            'ErrorMessage': f'Unknown device configuration type {device_type}'
        }, 404


@backend_bp.route('/reinitialize', methods=['PUT'])
def reinitialize():
    """Reinitialize SANE backend."""
    try:
        desanity.initialize()
        return {
            "initialized": True
        }, 200
    except DesanityException as ex:
        return {
            'ErrorMessage': f'Error reinitializing sane backend: {ex}'
        }, 500
