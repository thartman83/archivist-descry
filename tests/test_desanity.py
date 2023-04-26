###############################################################################
#  test_desanity.py for archivist descry microservice unit tests              #
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
"""Unit tests for the desanity class."""
# }}}
from unittest import mock
import random
import sane
from app.utils import desanity, DesanityUnknownDev, DesanityUnknownOption
from app.utils import DesanityOptionInvalidValue, DesanityOptionUnsettable
from .config import sane_devices
from .mocks import MockBrotherDev


@mock.patch.object(sane, "get_devices")
def test_get_devices(mock_sane):
    """
    GIVEN an initialized desanity Object
    WHEN devices is called
    SHOULD see that sane.get_devices is called
    """
    desanity.initialize()

    mock_sane.return_value = [sane_devices["brother"]]

    devices = desanity.available_devices

    assert "brother4:net1;dev0" in devices


@mock.patch.object(sane, "get_devices")
@mock.patch.object(desanity, "refresh_devices", wraps=desanity.refresh_devices)
def test_refresh_devices(mock_refresh_devices, mock_sane):
    """
    GIVEN an initialized desanity object
    WHEN devices is called
    SHOULD see that refresh_devices is called once
    SHOULD see that sane.get_devices is called once
    """
    desanity.initialize()
    mock_sane.return_value = [sane_devices["brother"]]

    devices = desanity.available_devices

    assert "brother4:net1;dev0" in devices
    mock_sane.assert_called_once()
    mock_refresh_devices.assert_called_once()


@mock.patch.object(sane, "get_devices")
@mock.patch.object(desanity, "refresh_devices", wraps=desanity.refresh_devices)
def test_get_devices_multiple(mock_refresh_devices, mock_sane):
    """
    GIVEN an initialized desanity object
    WHEN devices is called multiple times
    SHOULD see that refresh_devices is called once
    SHOULD see that sane.get_devices is called once
    """
    desanity.initialize()
    mock_sane.return_value = [sane_devices["brother"]]

    for _ in range(2, random.randint(3, 7)):
        devices = desanity.available_devices

    assert "brother4:net1;dev0" in devices
    mock_refresh_devices.assert_called_once()


@mock.patch.object(sane, "get_devices")
def test_open_device_not_found(mock_sane):
    """
    GIVEN an initialized desanity object
    GIVEN sane devices found
    WHEN open_device is called with a non-existant device
    SHOULD throw an Desanity Exception
    """
    desanity.initialize()
    mock_sane.return_value = [sane_devices["brother"]]

    error_found = False
    try:
        desanity.open_device("epson:dev12")
    except DesanityUnknownDev:
        error_found = True

    assert error_found


@mock.patch.object(sane, "get_devices")
@mock.patch.object(sane, "open")
def test_open_device(mock_open, mock_devices):
    """
    GIVEN an initialized desanity object
    GIVEN sane devices found
    WHEN open_device is called with an existing device
    SHOULD add an entry into the open device property
    """
    desanity.initialize()
    mock_devices.return_value = [sane_devices["brother"]]
    device_name = "brother4:net1;dev0"
    mock_open.return_value = device_name

    desanity.refresh_devices()
    desanity.open_device(device_name)
    assert "brother4_net1_dev0" in desanity.open_devices()


@mock.patch.object(sane, "get_devices")
@mock.patch.object(sane, "open")
def test_open_device_common_name(mock_open, mock_devices):
    """
    GIVEN an initialized desanity object
    GIVEN sane devices found
    WHEN open_device is called with an existing device
    SHOULD add an entry into the open device property
    """
    desanity.initialize()
    mock_devices.return_value = [sane_devices["brother"]]
    device_name = "brother4:net1;dev0"
    mock_open.return_value = device_name

    desanity.refresh_devices()
    desanity.open_device(device_name, "brother4")
    assert "brother4" in desanity.open_devices()


@mock.patch.object(sane, "get_devices")
@mock.patch.object(sane, "open")
def test_device_options(mock_open, mock_devices):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN device_options is called with an existing device
    SHOULD return a parsed set of device options
    """
    desanity.initialize()
    device_name = "brother4:net1;dev0"
    mock_devices.return_value = [sane_devices["brother"]]
    mock_open.return_value = MockBrotherDev()
    desanity.open_device(device_name, device_name)

    parsed_options = desanity.device_options(device_name)

    assert len(parsed_options) == 12
    assert parsed_options[2]['Name'] == 'Scan mode'
    assert parsed_options[3]['propertyName'] == 'resolution'
    assert parsed_options[4]['type'] == 3
    assert isinstance(parsed_options[4]['constraints'], list)
    assert parsed_options[4]['constraints'][0] == 'FlatBed'
    assert isinstance(parsed_options[5]['constraints'], dict)
    assert parsed_options[5]['constraints']['min'] == -50


@mock.patch.object(sane, "get_devices")
@mock.patch.object(sane, "open")
def test_device_paramaters(mock_open, mock_devices):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN device_parameters is called with an existing device
    SHOULD return a parsed set of device parameters
    """
    desanity.initialize()
    device_name = "brother4:net1;dev0"
    mock_devices.return_value = [sane_devices["brother"]]
    mock_open.return_value = MockBrotherDev()
    desanity.open_device(device_name, device_name)

    parsed_params = desanity.device_parameters(device_name)

    assert parsed_params['format'] == 'color'
    assert parsed_params['last_frame'] == 1
    assert parsed_params['pixelPerLine'] == 1651
    assert parsed_params['lines'] == 2783
    assert parsed_params['depth'] == 8
    assert parsed_params['bytes_per_line'] == 4953


@mock.patch.object(sane, "get_devices")
@mock.patch.object(sane, "open")
def test_set_device_option(mock_open, mock_devices):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an existing device
    SHOULD set the sane parameter
    """
    desanity.initialize()
    device_name = "brother4:net1;dev0"
    mock_devices.return_value = [sane_devices["brother"]]
    mock_open.return_value = MockBrotherDev()
    desanity.open_device(device_name, device_name)

    option_name = "mode"
    value = "True Gray"

    try:
        desanity.set_device_option(device_name, option_name, value)
        passed = True
    except DesanityUnknownDev:
        passed = False

    assert passed


def test_set_device_optionr_unknown_device(mocker):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an unknown device
    SHOULD throw a DesanityUnknownDevice execption
    """
    desanity.initialize()

    mock_get_devies = mocker.patch.object(sane, "get_devices")
    mock_get_devies.return_value = [sane_devices["brother"]]

    mock_open_device = mocker.patch.object(sane, "open")
    mock_open_device.return_value = MockBrotherDev()

    try:
        desanity.set_device_option("epson", "mode", "True Gray")
        passed = False
    except DesanityUnknownDev:
        passed = True

    assert passed


def test_set_device_option_unknown_option(mocker):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an existing device
    WHEN the option is not available
    SHOULD throw a DesanityUnknownOption execption
    """
    desanity.initialize()

    mock_get_devies = mocker.patch.object(sane, "get_devices")
    mock_get_devies.return_value = [sane_devices["brother"]]

    mock_open_device = mocker.patch.object(sane, "open")
    mock_open_device.return_value = MockBrotherDev()

    desanity.refresh_devices()
    common_name = desanity.open_device('brother4:net1;dev0')

    try:
        desanity.set_device_option(common_name, "magic", "True Gray")
        passed = False
    except DesanityUnknownOption:
        passed = True

    assert passed


def test_set_device_option_invalid_value(mocker):
    """
    GIVEN an initialized desanity object
    GIVEN sane device found
    WHEN set_device_parameter is called for an existing device
    WHEN the option is not settable
    SHOULD throw a DesanityOptionUnsettable execption
    """
    desanity.initialize()

    mock_get_devies = mocker.patch.object(sane, "get_devices")
    mock_get_devies.return_value = [sane_devices["brother"]]

    mock_open_device = mocker.patch.object(sane, "open")
    mock_open_device.return_value = MockBrotherDev()

    desanity.refresh_devices()
    common_name = desanity.open_device('brother4:net1;dev0')

    try:
        desanity.set_device_option(common_name, "mode", "foo")
        passed = False
    except DesanityOptionInvalidValue:
        passed = True

    assert passed

# test_set_device_option_not_active
