###############################################################################
#  device_config.py for archivist descry microservice                         #
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
"""ORM for device configuration stored in redis."""
# }}}

# libraries {{{
from redis_om import EmbeddedJsonModel, JsonModel, Field
# }}}


# device_config {{{
class DeviceConfigOption(EmbeddedJsonModel):
    """JSON redis ORM for a SANE device option."""

    option_name: str = Field()
    option_value: str = Field()


class DeviceConfig(JsonModel):
    """JSON redis ORM for SANE device configuration."""

    device_name: str = Field()
    common_name: str = Field(index=True)
    options: list[DeviceConfigOption] = Field()

# }}}
