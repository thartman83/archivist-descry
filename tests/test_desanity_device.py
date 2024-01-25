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
from unittest import mock
from collections import UserDict
import sane
from tests.mocks.mockBrother import MockBrotherDev
from app.utils import DesanityDevice, DevStatus
from app.utils.desanityExceptions import DesanitySaneException
from app.utils.desanityExceptions import DesanityDeviceNotEnabled

SaneError = sane._sane.error
# }}}

# desanityDevice unit tests {{{
mock_sane_dev_parms = ('color', 1, (1651, 2783), 8, 4953)
mock_sane_dev_opt_keys = ['None', 'mode', 'resolution', 'source', 'brightness',
                          'contrast', 'tl_x', 'tl_y', 'br_x', 'br_y']


@mock.patch.object(sane, "open")
def test_enable(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN enable is called
    SHOULD call sane.open once
    SHOULD set status to enabled
    """

    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_open.return_value = "MockSaneDevice"
    dev.enable()

    assert dev.enabled
    assert dev.status == DevStatus.ENABLED
    mock_sane_open.assert_called_once()


@mock.patch.object(sane, "open")
def test_enable_error(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN enable is called
    WHEN sane raises an error
    SHOULD raise a DesanitySaneException
    """

    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_open.side_effect = SaneError()
    error_found = False
    try:
        dev.enable()
    except DesanitySaneException:
        error_found = True

    mock_sane_open.assert_called_once()
    assert error_found


@mock.patch.object(sane, "open")
def test_disable(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN disabled is called
    SHOULD set status to disabled
    """
    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_dev = mock.Mock()
    mock_sane_dev_close = mock.Mock()
    mock_sane_dev.close = mock_sane_dev_close
    mock_sane_open.return_value = mock_sane_dev

    dev.enable()

    dev.disable()
    assert dev.enabled is False
    assert dev.status == DevStatus.DISABLED
    mock_sane_dev_close.assert_called_once()


@mock.patch.object(sane, "open")
def test_parameters(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN parameters is called
    SHOULD return the list of paramters in a dictionary
    """
    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_dev = mock.Mock()
    mock_sane_dev_get_parameters = mock.Mock(return_value=mock_sane_dev_parms)
    mock_sane_dev.get_parameters = mock_sane_dev_get_parameters
    mock_sane_open.return_value = mock_sane_dev

    dev.enable()

    params = dev.parameters
    mock_sane_dev_get_parameters.assert_called_once()
    assert params['format'] == 'color'
    assert params['last_frame'] == 1
    assert params['pixelPerLine'] == 1651
    assert params['lines'] == 2783
    assert params['depth'] == 8
    assert params['bytes_per_line'] == 4953


@mock.patch.object(sane, "open")
def test_parameters_not_enabled(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN the device is not enabled
    WHEN parameters is called
    SHOULD raise a DesanityDeviceNotEnabled error
    """
    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_dev = mock.Mock()
    mock_sane_dev_get_parameters = mock.Mock(return_value=mock_sane_dev_parms)
    mock_sane_dev.get_parameters = mock_sane_dev_get_parameters
    mock_sane_open.return_value = mock_sane_dev

    error_found = False
    try:
        dev.parameters
    except DesanityDeviceNotEnabled:
        error_found = True

    assert error_found


@mock.patch.object(sane, "open")
def test_parameters_sane_error(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN the device is enabled
    WHEN parameters is called
    WHEN sane raises an error
    SHOULD raise a SaneException error
    """
    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_dev = mock.Mock()
    mock_sane_dev_get_parameters = mock.Mock(side_effect=SaneError())
    mock_sane_dev.get_parameters = mock_sane_dev_get_parameters
    mock_sane_open.return_value = mock_sane_dev

    dev.enable()

    error_found = False
    try:
        dev.parameters
    except DesanitySaneException:
        error_found = True

    assert error_found


@mock.patch.object(sane, "open")
def test_get_options(mock_sane_open):
    """
    GIVEN a DesanityDevice
    WHEN get_options is called
    SHOULD return a json dictionary of available options
    """
    dev = DesanityDevice("aScanner", "ACME Corp", "B", "ABCDEF")

    mock_sane_dev = MockBrotherDev()
    mock_sane_open.return_value = mock_sane_dev

    dev.enable()
    options = dev.options

    assert len(options.keys()) == 15
    assert dev.option

# get options
# set option
# scan
