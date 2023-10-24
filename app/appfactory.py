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
"""Appfactory pattern implementation."""
# }}}

# appfactory # {{{
import sys
from flask import Flask
from flask_cors import CORS
from app.routes.airscan import airscan_bp
from app.routes.devices import devices_bp
from app.routes.initialize import init_bp
from app.routes.spec import spec_bp
from app.routes.docs import swaggerui_bp


def create_app(cfg):
    """Create an archivist descry application.

    Keyword arguments:
    cfg -- configuration object
    """
    app = Flask(__name__)
    app.config.from_object(cfg)
    api_routes = '/api/v1'

    # register the route blueprints
    app.register_blueprint(devices_bp, url_prefix=f"{api_routes}/devices")
    app.register_blueprint(init_bp, url_prefix=f"{api_routes}/init")
    app.register_blueprint(swaggerui_bp, url_prefix=f"{api_routes}/docs")
    app.register_blueprint(spec_bp, url_prefix=f"{api_routes}/spec")
    app.register_blueprint(airscan_bp, url_prefix=f"{api_routes}/airscan")

    print(app.url_map)

    CORS(app)

    return app
# }}}
