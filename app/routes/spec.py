###############################################################################
#  spec.py for archivist card catalog microservice                            #
#  Copyright (c) 2022 Tom Hartman (thomas.lees.hartman@gmail.com)             #
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

# Description {{{
"""OpenAPI specification."""
# }}}

# Spec routes {{{
import yaml
from flask import Blueprint

spec_bp = Blueprint('spec', __name__, url_prefix='/spec')


@spec_bp.route('', methods=['GET'])
def get_spec():
    """Get the microservice speification."""
    with open("openapi.yml", "r", encoding='utf-8') as yaml_in:
        yaml_def = yaml.safe_load(yaml_in)
        return yaml_def, 200

# }}}
