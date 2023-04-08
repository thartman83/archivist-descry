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
from enum import IntEnum
import sane
# }}}


# desanity # {{{

# typedef the sane exception for easier readability
SaneError = sane._sane.error


# options enums
class DevOptions(IntEnum):
    """Sane device enumeration."""

    PROP_NAME = 1
    NAME = 2
    DESCRIPTION = 3
    TYPE = 4
    UNIT = 5
    SIZE = 6
    CAP = 7
    CONSTRAINTS = 8


class DevParams(IntEnum):
    """Sane device parameters."""

    FORMAT = 0
    LAST_FRAME = 1
    RESOLUTION = 2
    DEPTH = 3
    BYTES_PER_LINE = 4


class Desanity():
    """Main utilty object providing SANE libray functionality."""

    def __init__(self):
        """Construct for the Desanity object."""
        self._initialized = False
        self._sane_version = None
        self._devices = None
        self._open_devices = {}
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

        if self._devices is None:
            self.refresh_devices()

        return self._devices

    def get_device(self, device_name):
        """Return the current open device."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if device_name not in self.open_devices():
            raise DesanityException(f"Device '{device_name}' is not opened")

        return {
            "name": device_name,
            "options": self.device_options(device_name),
            "parameters": self.device_parameters(device_name)
        }

    def device_options(self, device_name):
        """Return the options available for device {device_name}."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if device_name not in self.open_devices():
            raise DesanityException(f"Device {device_name} not opened")

        # parse the option tuples
        dev = self.open_devices()[device_name]
        options = dev.get_options()
        ret = []
        for opt in options:
            # parse the constraints option
            constraints = self._parse_constraints(
                opt[DevOptions.CONSTRAINTS])

            # parse the property name and value
            prop_name, prop_value = self._parse_name_value(
                opt[DevOptions.PROP_NAME], dev)

            ret.append({
                'propertyName': prop_name,
                'Name': opt[DevOptions.NAME],
                'Description': opt[DevOptions.DESCRIPTION],
                'type': opt[DevOptions.TYPE],
                'unit': opt[DevOptions.UNIT],
                'size': opt[DevOptions.SIZE],
                'cap': opt[DevOptions.CAP],
                'constraints': constraints,
                'value': prop_value
            })

        return ret

    def device_parameters(self, device_name):
        """Return the device parameters for device {device_name}."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if device_name not in self.open_devices():
            raise DesanityException(f"Device {device_name} not opened")

        parameters = self.open_devices()[device_name].get_parameters()

        return {
            'format': parameters[DevParams.FORMAT],
            'last_frame': parameters[DevParams.LAST_FRAME],
            'pixelPerLine': parameters[DevParams.RESOLUTION][0],
            'lines': parameters[DevParams.RESOLUTION][1],
            'depth': parameters[DevParams.DEPTH],
            'bytes_per_line': parameters[DevParams.BYTES_PER_LINE]
        }

    def initialize(self):
        """Initialize SANE engine."""
        self._sane_version = sane.init()
        self._initialized = True
        self._devices = None

        return self.sane_version

    def refresh_devices(self):
        """Refresh/get the list of sane devices."""
        self._devices = sane.get_devices()

        return self._devices

    def open_device(self, device_name):
        """Open a sane device."""
        if not self.initialized:
            raise DesanityException("Not initialized")

        if self._devices is None:
            self.refresh_devices()

        if device_name not in self.open_devices():
            raise DesanityException(f"Unknown device {device_name}")

        self._open_devices[device_name] = sane.open(device_name)

    def open_devices(self):
        """Return the list of open devices within desanity."""
        if not self.initialized:
            raise DesanityException("Not initialized")

        if self._devices is None:
            self.refresh_devices()

        return list(map(lambda device: device[0], self._devices))

    def _parse_constraints(self, opt):
        """Return the constraits for the given option."""
        if opt is None:
            constraints = None
        elif isinstance(opt, tuple):
            constraints = {
                'min': opt[0],
                'max': opt[1],
                'step': opt[2]
            }
        elif isinstance(opt, list):
            constraints = opt
        else:
            constraints = None

        return constraints

    def _parse_name_value(self, opt, dev):
        """Parse the property name and value from the option."""
        if opt is not None:
            property_name = opt.replace('-', '_')

            if dev[property_name].is_active():
                value = repr(getattr(dev, property_name))
            else:
                value = None
        else:
            property_name = None
            value = None

        return property_name, value


class DesanityException(Exception):
    """Raise when a SANE issue occurs."""


desanity = Desanity()
# }}}
