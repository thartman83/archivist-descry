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
from flask import Blueprint
# from flask import request
from app.utils import Desanity, DesanityException
# }}}

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


@devices_bp.route('', methods=['GET'])
def get_devices():
    """Retrieve a list of devices from the sane."""
    try:
        devices = Desanity.devices
    except DesanityException as ex:
        raise ex

    return {
        'Ok': True,
        'devices': devices
    }, 200
