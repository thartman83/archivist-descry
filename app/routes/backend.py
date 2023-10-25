###############################################################################
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
    """
    Get the decry backend configuration.
    """
    try:
        return {
            'devices': desanity.available_devices
        }, 200
    except DesanityException as ex:
        return {}, 500


@backend_bp.route('/discover_device', methods=['GET'])
def get_devices():
    """
    Discover available devices to Descry.
    """
    try:
        return desanity.refresh_devices(), 200
    except AttributeError as ex:
        return {}, 500
    except DesanityException as ex:
        return {}, 500


@backend_bp.route('/discover_device', methods=['PUT'])
def configure_device():
    """
    Configure a new Descry device.
    """
    try:
        req = None if not request.is_json else request.get_json()
    except DesanityException as ex:
        return {}, 500


@backend_bp.route('/reinitialize', methods=['PUT'])
def reinitialize():
    """
    Reinitialize SANE backend.
    """
    try:
        desanity.initialize()
        return { "initialized": True }, 200
    except:
        return {}, 500
