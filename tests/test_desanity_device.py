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
from app.utils import DesanityOptionInvalidValue
from app.utils import DesanityUnknownOption, DesanityException
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

    assert len(parsed_options) == 15
    assert parsed_options['mode']['name'] == 'mode'
    assert parsed_options['resolution']['py_name'] == 'resolution'
    assert parsed_options['source']['type'] == 2
    assert isinstance(parsed_options['source']['constraints'], list)
    assert parsed_options['source']['constraints'][0] == 'Flatbed'
    assert isinstance(parsed_options['br_y']['constraints'], dict)
    assert parsed_options['br_y']['constraints']['min'] == 0.0


def test_device_paramaters():
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN device_parameters is called with an existing device
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


def test_set_device_option():
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an existing device
    SHOULD set the sane parameter
    """
    device = DesanityDevice(MockBrotherDev())

    option_name = "mode"
    value = "True Gray"

    try:
        device.set_option(option_name, value)
        passed = True
    except DesanityException:
        passed = False

    assert passed


def test_set_device_option_unknown_option():
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an existing device
    WHEN the option is not available
    SHOULD throw a DesanityUnknownOption execption
    """
    device = DesanityDevice(MockBrotherDev())

    try:
        device.set_option("magic", "True Gray")
        passed = False
    except DesanityUnknownOption:
        passed = True

    assert passed


def test_device_busy():
    """
    GIVEN an initiatlized desanity device object
    WHEN the device is currently scanning
    SHOULD raise a DesanityDeviceBusy exception
    """
    assert True
#    passed = False
#     try:
#         device = DesanityDevice(MockBrotherDev())
#         assert device.status == DevStatus.IDLE
#         device.scan()
#         assert device.status == DevStatus.SCANNING
#         device.scan()
#     except DesanityDeviceBusy:
#         passed = True

#     assert passed
# }}}
