###############################################################################
#  desanity.py for archivist descry microservices                             #
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
"""
Sane utility object.

Provides functionality for SANE scanning operations. Implemented as
a singleton object.
"""
# }}}

# libraires {{{
import configparser
import sane
from flask import current_app
from .desanityDevice import DesanityDevice
from .desanityExceptions import DesanityUnknownDev, SaneException
from .desanityExceptions import DesanitySaneException
# }}}


# desanity # {{{
class Desanity():
    """Main utilty object providing SANE libray functionality."""

    sane_version: str
    sene_devices: list
    _devices: []

    def __init__(self) -> None:
        """Construct for the Desanity object."""
        self._devices = []
        self.initialize()

    @property
    def sane_version(self) -> str:
        """Return the version of the SANE object."""
        return self._sane_version

    @property
    def devices(self) -> list:
        """Return the list of devices from SANE."""
        return self._devices

    def initialize(self):
        """Initialize SANE engine.

        returns: A string
        raises: DesanitySaneException
                If a sane error occurs.
        """
        # clean up the sane backend state
        self._delete_devices()
        sane.exit()

        try:
            self._sane_version = sane.init()
        except SaneException as ex:
            raise DesanitySaneException(str(ex)) from ex
        return self.sane_version

    def refresh_devices(self):
        """Refresh/get the list of sane devices."""
        try:
            devices = sane.get_devices()
        except SaneException as ex:
            raise DesanitySaneException(str(ex)) from ex

        self._delete_devices()
        self._devices = list(map(lambda dev_info:
                                 DesanityDevice(dev_info[0], dev_info[1],
                                                dev_info[2], dev_info[3]),
                                 devices))
        return self._devices

    def get_device(self, device_name):
        """Return the open Desanity Device."""
        try:
            ret = next((d for d in self._devices if d.name == device_name))
        except StopIteration as ex:
            raise DesanityUnknownDev(f'Unknown device {device_name}') from ex

        return ret

    def add_device_by_url(self, device_name, device_url, device_type):
        """Add a device configuration by url.

        Throws IOError, KeyError
        """
        conf = configparser.ConfigParser()
        conf_file = current_app.config['CONFIG'][device_type]

        with open(conf_file, encoding="utf-8") as conf_fp:
            conf.read_file(conf_fp)

        conf.read(conf_file)
        conf.set('devices', f'"{device_name}"', device_url)

        with open(conf_file, encoding="utf-8", mode="w") as conf_fp:
            conf.write(conf_fp)

        return {
            'conf': {
                'devices': dict(conf['devices']),
                'options': dict(conf['options']),
                'debug': dict(conf['debug'])
            }
        }

    def get_device_configs(self, device_type):
        """Get device configuration from the backend.

        Throws IOError
        """
        conf = configparser.ConfigParser()
        conf_file = current_app.config['CONFIG'][device_type]

        with open(conf_file, encoding="utf-8") as conf_fp:
            conf.read_file(conf_fp)

        conf.read(conf_file)

        return {
            'conf': {
                'devices': dict(conf['devices']),
                'options': dict(conf['options']),
                'debug': dict(conf['debug'])
            }
        }

    def _delete_devices(self):
        """Close and remove all existing devices."""
        map(lambda dev: dev.disable(), self._devices)
        self._devices = []


desanity = Desanity()
# }}}
