###############################################################################
#  mockBrother.py for archivist descry microservice tests mocks               #
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
"""Mock brother scanner device."""
# }}}

# mockBrother {{{

brother_options = [
    (0, None, 'Number of options',
     'Read-only option that specifies how many options a specific devices supports.',
     0, 0, 4, 4, None),
    (1, None, 'Mode', '', 5, 0, 4, 64, None),
    (2, 'mode', 'Scan mode', 'Select the scan mode', 3, 0, 30, 5,
     ['Black & White', 'Gray[Error Diffusion]', 'True Gray', '24bit Color',
      '24bit Color[Fast]']),
    (3, 'resolution', 'Scan resolution',
     'Sets the resolution of the scanned image.', 1, 4, 4, 5,
     [100, 150, 200, 300, 400, 600, 1200, 2400, 4800, 9600]),
    (4, 'source', 'Scan source',
     'Selects the scan source (such as a document-feeder).', 3, 0, 64, 5,
     ['FlatBed', 'Automatic Document Feeder(left aligned)',
      'Automatic Document Feeder(left aligned,Duplex)',
      'Automatic Document Feeder(centrally aligned)',
      'Automatic Document Feeder(centrally aligned,Duplex)']),
    (5, 'brightness', 'Brightness',
     'Controls the brightness of the acquired image.', 2, 5, 4, 37,
     (-50.0, 50.0, 1.0)),
    (6, 'contrast', 'Contrast', 'Controls the contrast of the acquired image.',
     2, 5, 4, 37, (-50.0, 50.0, 1.0)),
    (7, None, 'Geometry', '', 5, 0, 4, 64, None),
    (8, 'tl-x', 'Top-left x', 'Top-left x position of scan area.', 2, 3, 4, 5,
     (0.0, 211.89999389648438, 0.0999908447265625)),
    (9, 'tl-y', 'Top-left y', 'Top-left y position of scan area.', 2, 3, 4, 5,
     (0.0, 355.59999084472656, 0.0999908447265625)),
    (10, 'br-x', 'Bottom-right x', 'Bottom-right x position of scan area.', 2,
     3, 4, 5, (0.0, 211.89999389648438, 0.0999908447265625)),
    (11, 'br-y', 'Bottom-right y', 'Bottom-right y position of scan area.', 2,
     3, 4, 5, (0.0, 355.59999084472656, 0.0999908447265625))]

brother_parameters = ('color', 1, (1651, 2783), 8, 4953)


class MockBrotherDev():
    """A mocked dev object."""

    def __getitem__(self, item):
        """Return property."""
        return MockBrotherDevProperty()

    def get_options(self):
        """Return mock device options."""
        return brother_options

    def get_parameters(self):
        """Return mock device parameters."""
        return brother_parameters


class MockBrotherDevProperty():
    """A mocked sane dev property object."""

    def is_active(self):
        """Return if the given property is active or not."""
        return True

# }}}
