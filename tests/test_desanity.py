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
from app.utils import desanity, DesanityException
from .config import sane_devices


def test_get_devices_no_init():
    """
    GIVEN a desanity Object
    WHEN desanity isn't initialied
    WHEN devices is called
    SHOULD throw a DesanityException
    """
    threw_exception = False

    try:
        desanity.devices
    except DesanityException:
        threw_exception = True

    assert threw_exception


def test_initialized():
    """
    GIVEN a desanity Object
    WHEN desanity isn't initialized
    SHOULD return False when Initialized is called
    """
    assert not desanity.initialized


@mock.patch.object(sane, "get_devices")
def test_get_devices(mock_sane):
    """
    GIVEN an initialized desanity Object
    WHEN devices is called
    SHOULD see that sane.get_devices is called
    """
    desanity.initialize()

    mock_sane.return_value = [sane_devices["brother"]]

    devices = desanity.devices

    assert devices[0][0] == "brother4:net1;dev0"


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

    devices = desanity.devices

    assert devices[0][0] == "brother4:net1;dev0"
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

    for _ in range(2, random.randint(2, 7)):
        devices = desanity.devices

    assert devices[0][0] == "brother4:net1;dev0"
    mock_sane.assert_called_once()
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
    except DesanityException:
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
    assert "brother4:net1;dev0" in desanity.open_devices()
