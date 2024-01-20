###############################################################################
#  desanityExceptions.py for archivist-descry microservice                    #
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

# Commentary {{{
"""Exceptions for Desanity classes."""
# }}}

# Desanity Exceptions {{{
import sane
SaneException = sane._sane.error


class DesanityException(Exception):
    """Raise when a SANE issue occurs."""


class DesanitySaneException(DesanityException):
    """Sane Error."""


class DesanityUnknownDev(DesanityException):
    """Unknown device referenced."""


class DesanityDeviceBusy(DesanityException):
    """The SANE device is busy."""


class DesanityDeviceNotEnabled(DesanityException):
    """Desanity Device not enabled."""


class DesanityOptionInvalidValue(DesanityException):
    """Invalid value for SANE device option."""


class DesanityOptionUnsettable(DesanityException):
    """SANE option not settable."""


class DesanityUnknownOption(DesanityException):
    """Option does not exist for sane device."""
# }}}
