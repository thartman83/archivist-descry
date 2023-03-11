###############################################################################
#  appfactory.py for archivist card catalog microservice                      #
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
"""
Appfactory pattern implementation
"""
# }}}

# appfactory # {{{
from flask import Flask
from flask_cors import CORS


def create_app(cfg):
    """Create an archivist descry application

    Keyword arguments:
    cfg -- configuration object
    """
    app = Flask(__name__)
    app.config.from_object(cfg)

    CORS(app)

    return app
# }}}
