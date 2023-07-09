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
from flask import Flask, jsonify
from flask_swagger import swagger
from flask_cors import CORS
from app.routes.devices import devices_bp
from app.routes.initialize import init_bp
from app.routes.docs import swaggerui_bp


def create_app(cfg):
    """Create an archivist descry application.

    Keyword arguments:
    cfg -- configuration object
    """
    app = Flask(__name__)
    app.config.from_object(cfg)

    # register the route blueprints
    app.register_blueprint(devices_bp)
    app.register_blueprint(init_bp)
    app.register_blueprint(swaggerui_bp)

    # Add swagger
    @app.route('/api/spec')
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "0.1"
        swag['info']['title'] = "Descry"
        swag['info']['description'] = "Scanning microservice"
        return jsonify(swag)

    CORS(app)

    return app
# }}}
