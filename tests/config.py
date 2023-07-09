###############################################################################
#  config.py for archivist descry microservice tests                          #
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

# Commentary {{{
"""Default test configuration."""
# }}}

# config {{{
from app.config import AppConfig


class TestConfig(AppConfig):  # pylint: disable=too-few-public-methods
    """Configuration object for running card catalog unit tests."""

    dbEngine = "sqlite"
    dbHost = "localhost"
    dbName = "card-catalog"
    dbUser = ""
    dbPasswd = ""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# example sane devices
sane_devices = {
    "blank": [],
    "brother": ("brother4:net1;dev0", "Brother", "*MFC-L2700DW",
                "BROTHER_MFC-L2700DW_series"),
    "camera": ("v4l:/dev/video0", "Noname", "Integrated Camera: Integrated C",
               "virtual device")
}
