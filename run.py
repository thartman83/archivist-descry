###############################################################################
#  run.py for archivist descry microservices                                  #
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
"""Main entry point for the descry microservice."""
# }}}


# run # {{{
import os
from app import create_app, Configs

if __name__ == "__main__":
    configType = os.environ.get('APPCONFIG') or "DEV"
    config = {}
    try:
        config = Configs[configType]()
    except KeyError:
        print(f"Unknown configuration type {configType}")

    app = create_app(config)
    app.run(host='0.0.0.0')

# }}}
