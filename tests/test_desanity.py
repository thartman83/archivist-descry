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
# import random
import sane
from app.utils import DesanityDevice
from app.utils.desanityExceptions import DesanitySaneException
from app.utils.desanityExceptions import DesanityUnknownDev
SaneError = sane._sane.error
# from app.utils import desanity, DesanityUnknownDev
# from .config import sane_devices

mock_sane_devices = [('brother4:net1;dev0', 'Brother', '*MFC-L2700DW',
                      'BROTHER_MFC-L2700DW_series'),
                     ('v4l:/dev/video0', 'Noname',
                      'Integrated Camera: Integrated C', 'virtual device'),
                     ('airscan:w1:Brother MFC-L2700DW series', 'WSD',
                      'Brother MFC-L2700DW series', 'ip=172.17.1.28')]


@mock.patch.object(sane, "init")
@mock.patch.object(sane, "exit")
def test_initialize(mock_sane_exit, mock_sane_init):
    """
    GIVEN a desanity Object
    WHEN initialize is called
    SHOULD see that self._delete_devices() is called
    SHOULD see that sane.exit() is called
    SHOULD see that sane.init() is called
    SHOULD return sane version.
    """
    from app.utils import desanity

    sane_version = "1.00"
    mock_sane_init.return_value = sane_version

    desanity.initialize()

    mock_sane_init.assert_called_once()
    mock_sane_exit.assert_called_once()
    assert isinstance(desanity.sane_version, str)
    assert desanity.sane_version == sane_version


@mock.patch.object(sane, "init")
def test_initialize_bad_init(mock_sane_init):
    """
    GIVEN a desanity object
    WHEN initialize is called
    WHEN sane raises an exception
    SHOULD see that a DesanitySaneException is raised.
    """

    from app.utils import desanity

    mock_sane_init.side_effect = SaneError('init error')
    error_found = False
    try:
        desanity.initialize()
    except DesanitySaneException:
        error_found = True

    assert error_found


@mock.patch.object(sane, "get_devices")
def test_refresh_devices(mock_sane_get_devices):
    """
    GIVEN an initialized desanity object
    WHEN get_devices is called
    SHOULD see delete_devices is called
    SHOULD see that devices property is set with the appropriate objects
    """
    mock_sane_get_devices.return_value = mock_sane_devices

    from app.utils import desanity
    desanity._delete_devices = mock.Mock()

    devs = desanity.refresh_devices()
    desanity._delete_devices.assert_called_once()
    assert isinstance(devs, list)
    assert len(devs) == 3
    assert all(map(lambda it: isinstance(it, DesanityDevice), devs))


@mock.patch.object(sane, "get_devices")
def test_refresh_devices_sane_error(mock_sane_get_devices):
    """
    GIVEN an initialized desanity object
    WHEN get_devices raises an exception
    SHOULD raise a DesanitySaneException
    """
    mock_sane_get_devices.side_effect = SaneError('get_device error')

    from app.utils import desanity

    desanity.initialize()
    error_found = False
    try:
        desanity.refresh_devices()
    except DesanitySaneException:
        error_found = True

    assert error_found


@mock.patch.object(sane, "get_devices")
def test_get_device(mock_sane_get_devices):
    """
    GIVEN an initialized desanity object
    WHEN get_device is called
    WHEN device exists
    SHOULD return a DesanityDevice
    """
    mock_sane_get_devices.return_value = mock_sane_devices

    from app.utils import desanity

    desanity.initialize()
    desanity.refresh_devices()

    dev = desanity.get_device("brother4:net1;dev0")
    assert isinstance(dev, DesanityDevice)


@mock.patch.object(sane, "get_devices")
def test_refresh_unknown_device(mock_sane_get_devices):
    """
    GIVEN an initialized desanity object
    WHEN get_device is called
    WHEN device does not exist
    SHOULD raise a DesanityUnknownDev
    """
    mock_sane_get_devices.return_value = mock_sane_devices

    from app.utils import desanity

    desanity.initialize()
    desanity.refresh_devices()
    error_found = False

    try:
        desanity.get_device("SomeUnknownDevice")
    except DesanityUnknownDev:
        error_found = True

    assert error_found
