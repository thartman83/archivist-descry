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
        self._sane_version = None
        self._devices = []
        self._open_devices = {}
        self._parameters = None

        sane.init()

    @property
    def sane_version(self):
        """Return the version of the SANE object."""
        return self._sane_version

    @property
    def available_devices(self):
        """Return the list of devices from SANE."""
        if not self._devices:
            self.refresh_devices()
        return list(map(lambda device: device[0], self._devices))

    def device_options(self, device_name):
        """Return the options available for device {device_name}."""
        if device_name not in self.open_devices():
            raise DesanityUnknownDev(f"Device {device_name} not opened")

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

    def set_device_option(self, device_name, option_name, value):
        """Set a SAne device option."""
        if device_name not in self.open_devices():
            raise DesanityUnknownDev(f"Device {device_name} not opened")

        dev = self._devices['device_name']

        if option_name not in list(map(lambda opt: opt[DevOptions.PROP_NAME],
                                       self.device_options(device_name))):
            raise DesanityException(f"Option {option_name} not found for"
                                    "device {device_name}")

        dev.setattr(option_name, value)

    def device_parameters(self, device_name):
        """Return the device parameters for device {device_name}."""
        if device_name not in self.open_devices():
            raise DesanityUnknownDev(f"Device {device_name} not opened")

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
        self._sane_version = None
        self._devices = []
        self._open_devices = {}
        self._parameters = None

        return self.sane_version

    def refresh_devices(self):
        """Refresh/get the list of sane devices."""
        self._devices = sane.get_devices()

        return self._devices

    def open_device(self, device_name, common_name=None):
        """Open a sane device."""
        if not self._devices:
            self.refresh_devices()

        if common_name is None:
            common_name = self._replace_url_characters(device_name)

        if device_name not in self.available_devices:
            raise DesanityUnknownDev(f"Unknown device {device_name}")

        # if the device is already opened just return the common name
        if common_name in self._open_devices:
            return common_name

        self._open_devices[common_name] = sane.open(device_name)

        return common_name

    def open_devices(self):
        """Return the list of open devices within desanity."""
        if self._open_devices is None:
            return []

        return self._open_devices.keys()

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

    def _replace_url_characters(self, url_string):
        """Replace illegal url characters with an undescore."""
        retval = url_string
        illegal_chars = [";", "/", "?", ":", "@", "&",
                         "=", "+", "$", ",", "{", "}",
                         ",", '"', "^", "[", "]", "`"]
        for char in illegal_chars:
            retval = retval.replace(char, '_')

        return retval


class DesanityException(Exception):
    """Raise when a SANE issue occurs."""


class DesanityUnknownDev(DesanityException):
    """Unknown device referenced."""


desanity = Desanity()
# }}}
