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
"""Initialize route for the descry microservice."""
# }}}

# initialize # {{{
from flask import Blueprint, request
from app.utils import Desanity, DesanityException
# jsonify

init_bp = Blueprint('initialize', __name__, url_prefix='/initialize')


@init_bp.route('', methods=['GET'])
def get_configuration():
    """Retrive the current configuration for descry."""
    try:
        Desanity.initialize()
    except DesanityException:
        return {
            'Ok': False,
            'ErrMsg': """An exception occured while attempting to initialize
                         the sane environment"""
        }, 200

    return {
        'Ok': True,
    }, 200


@init_bp.route('', methods=['POST'])
def set_configuration():
    """Set the descry configuration."""
#    request_data = request.get_json()

    return {
        'Ok': False,
        'ErrMsg': 'Error, not implemented'
    }, 200

# }}}
