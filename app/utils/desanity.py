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
# }}}


# desanity # {{{

# typedef the sane exception for easier readability
SaneError = sane._sane.error


class DesanitySingleton():
    """
    Main utilty object providing SANE libray functionality.

    This object is built as a singleton for the rest of the microservice.
    """

    def __init__(self):
        """Construct for the Desanity object."""
        self._initialized = False
        self._sane_version = None
        self._devices = None
        self._open_device = None
        self._parameters = None

    @property
    def initialized(self):
        """Return if Desanity has been initialized."""
        return self._initialized

    @property
    def sane_version(self):
        """Return the version of the SANE object."""
        return self._sane_version

    @property
    def devices(self):
        """Return the list of devices from SANE."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        self._devices = sane.get_devices()

        return self._devices

    @property
    def device(self):
        """Return the current open device."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if self._open_device is None:
            raise DesanityException("Current device not opened")

        return self._open_device

    @device.setter
    def open_device(self, device_name):
        """Open a SANE device."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self._devices is None:
            devices = self.devices

        filtered_devices = list(filter(lambda d: d[0] == device_name,
                                       devices))

        if len(filtered_devices) < 0:
            raise DesanityException(f"Unknown device: {device_name}")

        try:
            self._open_device = sane.open(filtered_devices[0][0])
        except SaneError as ex:
            raise ex

        return self._open_device

    @property
    def device_options(self):
        """Return the current open device options."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if self._open_device is None:
            raise DesanityException("Current device not opened")

        return self._open_device.opt

    def initialize(self):
        """Initialize SANE engine."""
        if not self.initialized:
            self._sane_version = sane.init()
            self._initialized = True

        return self.sane_version


class DesanityException(Exception):
    """Raise when a SANE issue occurs."""

# }}}
