###############################################################################
#  test_desanity_device.py for archivist descry microservice unit test        #
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
"""Unit tests for the desanity device class."""
# }}}

# Libraries {{{
# from unittest import mock
from app.utils import DesanityDevice, DesanityDeviceBusy, DevStatus
from .mocks import MockBrotherDev
# }}}

# desanityDevice unit tests {{{


def test_device_options():
    """
    GIVEN an initialized desanity device object
    WHEN options is called with an existing device
    SHOULD return a parsed set of device options
    """
    device = DesanityDevice(MockBrotherDev())

    parsed_options = device.options

    assert len(parsed_options) == 12
    assert parsed_options[2]['Name'] == 'Scan mode'
    assert parsed_options[3]['propertyName'] == 'resolution'
    assert parsed_options[4]['type'] == 3
    assert isinstance(parsed_options[4]['constraints'], list)
    assert parsed_options[4]['constraints'][0] == 'FlatBed'
    assert isinstance(parsed_options[5]['constraints'], dict)
    assert parsed_options[5]['constraints']['min'] == -50


def test_device_paramaters():
    """
    GIVEN an initialized desanity device object
    WHEN parameters is called with an existing device
    SHOULD return a parsed set of device parameters
    """
    device = DesanityDevice(MockBrotherDev())
    parsed_params = device.parameters

    assert parsed_params['format'] == 'color'
    assert parsed_params['last_frame'] == 1
    assert parsed_params['pixelPerLine'] == 1651
    assert parsed_params['lines'] == 2783
    assert parsed_params['depth'] == 8
    assert parsed_params['bytes_per_line'] == 4953


def test_device_busy():
    """
    GIVEN an initiatlized desanity device object
    WHEN the device is currently scanning
    SHOULD raise a DesanityDeviceBusy exception
    """
    try:
        device = DesanityDevice(MockBrotherDev())
        assert device.status == DevStatus.IDLE
        device.scan()

        assert device.status == DevStatus.SCANNING
        device.scan()
        assert False
    except DesanityDeviceBusy:
        assert True


# }}}
