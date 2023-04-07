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

    # def device(self, device_name):
    #     """Open a SANE device."""
    #     if not self.initialized:
    #         raise DesanityException("Not Initialized")

    #     if self._devices is None:
    #         devices = self.refresh_devices()
    #     else:
    #         devices = self._devices

    #     filtered_devices = list(filter(lambda d: d[0] == device_name,
    #                                    devices))

    #     if len(filtered_devices) < 0:
    #         raise DesanityException(f"Unknown device: {device_name}")

    #     try:
    #         self._open_device = sane.open(filtered_devices[0][0])
    #         self._device_name = device_name
    #     except SaneError as ex:
    #         raise ex

    #     return self._open_device

    def device_options(self, device_name):
        """Return the options available for a given device_name."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if device_name not in self.open_devices():
            raise DesanityException(f"Device {device_name} not opened")

        # parse the option tuples
        dev = self._open_devices[device_name]
        options = dev.get_options()
        ret = []
        for opt in options:
            if opt[8] is None:
                constraints = None
            elif isinstance(opt[8], tuple):
                constraints = {
                    'min': opt[8][0],
                    'max': opt[8][1],
                    'step': opt[8][2]
                }
            elif isinstance(opt[8], list):
                constraints = opt[8]
            else:
                constraints = None

            if opt[1] is not None:
                property_name = opt[1].replace('-', '_')
            else:
                property_name = None

            if opt[1] is not None:
                if dev[property_name].is_active():
                    value = repr(getattr(dev, property_name))
                else:
                    value = None
            else:
                value = None

            ret.append({
                'propertyName': property_name,
                'Name': opt[2],
                'Description': opt[3],
                'type': opt[4],
                'unit': opt[5],
                'size': opt[6],
                'cap': opt[7],
                'constraints': constraints,
                'value': value
            })

        return ret

    def device_parameters(self, device_name):
        """Return the current open device options."""
        if not self.initialized:
            raise DesanityException("Not Initialized")

        if self.devices is None:
            raise DesanityException("No devices found")

        if device_name not in self.open_devices():
            raise DesanityException(f"Device {device_name} not opened")

        parameters = self._open_devices[device_name].get_parameters()

        return {
            'format': parameters[0],
            'last_frame': parameters[1],
            'pixelPerLine': parameters[2][0],
            'lines': parameters[2][1],
            'depth': parameters[3],
            'bytes_per_line': parameters[4]
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


class DesanityException(Exception):
    """Raise when a SANE issue occurs."""


desanity = Desanity()
# }}}
