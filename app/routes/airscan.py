###############################################################################
#  airscan.py for archivist descry microservices                              #
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

# Module DocString ## {{{
"""CRUD operations for airscan configuration."""
# }}}

# libraries # {{{
import configparser
from flask import Blueprint, current_app, request
# }}}

airscan_bp = Blueprint('airscan', __name__, url_prefix='/airscan')


@airscan_bp.route('', methods=['GET'])
def get_airscan_conf():
    """
    Retrive the current.

    ---
    tags:
      - airscan
    responses:
      200:
        description: The current state of the airscan.conf file
      404:
        description: Airscan configuration could not be found
    """
    conf = configparser.ConfigParser()
    try:
        conf.read(current_app.config['AIRSCAN_CONF'])
    except IOError as err:
        return {
            'ErrMsg': f'Error while reading configuration file {str(err)}'
        }, 500

    return {
        'conf': {
            'devices': dict(conf['devices']),
            'options': dict(conf['options']),
            'debug': dict(conf['debug'])
        }
    }, 200


@airscan_bp.route('device', methods=['PUT'])
def add_airscan_device():
    """
    Add an airscan device configuration.

    ---
    tags:
      - airscan
    parameters:
      - name: name
        description: Name of the device configuration
        required: True
        type: string
      - name: url
        description: Device url configuration
        required: True
        type: string
    response:
      201:
        description: Device added to the configuration
    """
    req = None if not request.is_json else request.get_json()

    if req is None or 'name' not in req or 'url' not in req:
        return {
            'ErrMsg': 'Missing device data'
        }, 400

    conf = configparser.ConfigParser()
    try:
        with open(current_app.config['AIRSCAN_CONF'],
                  encoding="utf-8") as conf_fp:
            conf.read_file(conf_fp)
    except IOError as err:
        return {
            'ErrMsg': f"Error reading configuration file: {str(err)}"
        }, 500

    conf.read(current_app.config['AIRSCAN_CONF'])
    name = req['name']
    url = req['url']
    conf.set('devices', f'"{name}"', url)

    try:
        with open(current_app.config['AIRSCAN_CONF'],
                  encoding="utf-8", mode="w") as conf_fp:
            conf.write(conf_fp)
    except IOError as err:
        return {
            'ErrMsg': f"Error writing configuration file: {str(err)}"
        }, 500

    return {
        'conf': {
            'devices': dict(conf['devices']),
            'options': dict(conf['options']),
            'debug': dict(conf['debug'])
        }
    }, 201
