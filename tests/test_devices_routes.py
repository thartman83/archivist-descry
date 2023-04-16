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
from app.appfactory import create_app
from app.config import TestConfig
from .config import sane_devices
from app.utils.desanity import desanity
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
    assert resp.json['Ok']


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
    assert resp.json['Ok']


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
    mock_open_device.return_value = {'Ok': True,
                                     'device': 'brother4:net1;dev0'}
    resp = test_client.post('devices/open', json={"device_name":
                                                  "brother4:net1;dev0"},
                            content_type='application/json')

    assert resp.status_code == 200
    assert resp.json['Ok']


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

    assert resp.status_code == 200
    assert not resp.json['Ok']
    assert f"Error opening sane device {device}" in resp.json['ErrMsg']
# }}}
