###############################################################################
#  DesanityJob.py for the desanity microservice                               #
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
"""Desanity Jobs."""
# }}}

# libraries {{{
import uuid
from enum import IntEnum
from datetime import datetime
# }}}

# desanity job {{{


class JobStatus(IntEnum):
    """Sane job statuses."""

    STARTED = 0
    COMPLETED = 1
    ERROR = 2


class DesanityJob():
    """A Scanning job."""

    _guid = None
    _job_number = None
    _images = []
    _start_date = None
    _end_date = None
    _job_status = None
    _error_str = None

    def __init__(self, job_number):
        """Initiatlize the Job."""
        self._guid = str(uuid.uuid4())
        self._job_number = job_number
        self._start_date = datetime.now()
        self._job_status = JobStatus.STARTED

    @property
    def guid(self):
        """Return the guid of the job."""
        return self._guid

    @property
    def job_number(self):
        """Return the job number assoicated with the job."""
        return self._job_number

    @property
    def images(self):
        """Return the scanned images associated with the job."""
        return self._images

    @property
    def status(self):
        """Return the job status."""
        return self._job_status

    @property
    def start_date(self):
        """Return the job start date."""
        return self._start_date

    @property
    def end_date(self):
        """Return the job end date."""
        return self._end_date

    @property
    def error_str(self):
        """Return the error message of the job."""
        return self._error_str

    def add_image(self, image):
        """Add an image to the job."""
        self._images.append(image)

    def mark_complete(self):
        """Mark job as completed."""
        self._job_status = JobStatus.COMPLETED
        self._end_date = datetime.now()

    def mark_error(self, error_str):
        """Mark job as having errored."""
        self._job_status = JobStatus.ERROR
        self._end_date = datetime.now()
        self._error_str = error_str

    def serialize_json(self):
        """Serialize the desanity job in json format."""
        return {
            'guid': self.guid,
            'job_number': self.job_number,
            'images': self.images,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'job_status': self.status,
            'error_str': self.error_str
        }
# }}}
