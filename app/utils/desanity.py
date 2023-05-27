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
import sane
from .desanityDevice import DesanityDevice
from .desanityExceptions import DesanityUnknownDev
# }}}


# desanity # {{{
class Desanity():
    """Main utilty object providing SANE libray functionality."""

    sane_version: str
    sene_devices: list
    _devices: []
    _open_devices: dict

    def __init__(self) -> None:
        """Construct for the Desanity object."""
        sane.init()
        self.initialize()

    @property
    def sane_version(self) -> str:
        """Return the version of the SANE object."""
        return self._sane_version

    @property
    def available_devices(self) -> list:
        """Return the list of devices from SANE."""
        if not self._devices:
            self.refresh_devices()

        return list(map(lambda device: device[0], self._devices))

    def initialize(self):
        """Initialize SANE engine."""
        self._sane_version = None
        self._devices = []
        self._open_devices = {}

        return self.sane_version

    def refresh_devices(self):
        """Refresh/get the list of sane devices."""
        self._devices = sane.get_devices()

        return self._devices

    def open_device(self, device_name, common_name=None):
        """Open a sane device `device-name`."""
        if not self._devices:
            self.refresh_devices()

        if common_name is None:
            common_name = self._replace_url_characters(device_name)

        if device_name not in self.available_devices:
            raise DesanityUnknownDev(f"Unknown device {device_name}")

        # if the device is already opened just return the common name
        if common_name in self._open_devices:
            return common_name

        # open the sane device and add a Desanity Device to the list
        # of open devices
        self._open_devices[common_name] = DesanityDevice(
            sane.open(device_name))

        return common_name

    def open_devices(self):
        """Return the list of open devices within desanity."""
        if self._open_devices is None:
            return []

        return self._open_devices.keys()

    def get_open_device(self, common_name):
        """Return the open Desanity Device."""
        if common_name not in self.open_devices():
            raise DesanityUnknownDev()

        return self._open_devices[common_name]

    def _replace_url_characters(self, url_string):
        """Replace illegal url characters with an undescore."""
        retval = url_string
        illegal_chars = [";", "/", "?", ":", "@", "&",
                         "=", "+", "$", ",", "{", "}",
                         ",", '"', "^", "[", "]", "`"]
        for char in illegal_chars:
            retval = retval.replace(char, '_')

        return retval


desanity = Desanity()
# }}}
