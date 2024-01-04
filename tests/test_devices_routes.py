###############################################################################
#  test_device_routes.py for archivist descry microservices unit testing      #
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

# Docstring ## {{{
"""Unit tests for descry device routes."""
# }}}

# libraries # {{
import pytest
import sane
from app.utils.desanity import desanity
from app.appfactory import create_app
from app.config import TestConfig
from .config import sane_devices
from .mocks import MockBrotherDev
# }}}


# Module test_device_routes ## {{{
@pytest.fixture(scope='module', name='test_client')
def fixture_test_client():
    """Test client for tests."""
    app = create_app(TestConfig())

    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    client.post('/init')
    yield client

    ctx.pop()


def test_get_devices(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /devices is called
    SHOULD return a list of SANE devices.
    """
    mock_sane = mocker.patch.object(sane, "get_devices")
    mock_sane.return_value = [sane_devices["brother"]]
    resp = test_client.get('/devices')

    assert resp.status_code == 200


def test_get_devices_no_cache(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /devices is called
    WHEN no_cache is sent as true
    SHOULD return a list of SANE devices.
    """
    mock_sane = mocker.patch.object(sane, "get_devices")
    mock_sane.return_value = [sane_devices["brother"]]
    resp = test_client.get('/devices', data={" no_cache": True})

    assert resp.status_code == 200


def test_open_device(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /devices/open is invoked
    WHEN device_name is present and exists
    SHOULD open the device
    """
    mock_devices = mocker.patch.object(sane, "get_devices")
    mock_devices.return_value = [sane_devices["brother"]]

    mock_open_device = mocker.patch.object(desanity, "open_device")
    mock_open_device.return_value = "brother4_net1_dev0"
    resp = test_client.post('devices/open', json={"device_name":
                                                  "brother4:net1;dev0"},
                            content_type='application/json')

    assert resp.status_code == 201
    assert "brother4_net1_dev0" in resp.json['device_id']


def test_open_device_unknown(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /devices/open is invoked
    WHEN device_name is present and exists
    SHOULD open the device
    """
    mock_devices = mocker.patch.object(sane, "get_devices")
    mock_devices.return_value = [sane_devices["brother"]]
    device = "epson5:net1;dev0"
    resp = test_client.post('devices/open', json={"device_name": device},
                            content_type='application/json')

    assert resp.status_code == 404
    assert f"Sane device {device} not found" in resp.json['ErrMsg']


def test_get_open_device(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /device/open/{device_name} is invoked
    WHEN device is opened
    SHOULD return list of device options and parameters
    """
    desanity.initialize()
    device_name = "brother4:net1;dev0"
    mock_get_devices = mocker.patch.object(sane, "get_devices")
    mock_get_devices.return_value = [sane_devices["brother"]]

    mock_sane_open = mocker.patch.object(sane, "open")
    mock_sane_open.return_value = MockBrotherDev()

    desanity.refresh_devices()
    common_name = desanity.open_device(device_name)

    resp = test_client.get(f'devices/open/{common_name}')

    assert resp.status_code == 200


def test_get_open_device_unknown(test_client, mocker):
    """
    GIVEN a descry client
    WHEN /device/open/{device_name} is invoked
    WHEN device is not opened or doesn't exist
    SHOULD return list of device options and parameters
    """
    mock_devices = mocker.patch.object(sane, "get_devices")
    mock_devices.return_value = [sane_devices["brother"]]
    device_name = "epson5_net1_dev0"
    resp = test_client.get(f'devices/open/{device_name}')

    assert resp.status_code == 404
    assert f"Sane device {device_name} not found" in resp.json['ErrMsg']


# }}}
