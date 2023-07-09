###############################################################################
#  desanity Device.py for the desanity microservice                           #
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
"""Wrapper for SANE Device."""
# }}}

# libraries {{{
from threading import Thread
from enum import IntEnum
from datetime import datetime
from .desanityExceptions import DesanityDeviceBusy, DesanityOptionInvalidValue
from .desanityExceptions import DesanityUnknownOption, SaneException
# }}}

# desanity device {{{


class DevOptions(IntEnum):
    """Sane device enumeration."""

    PROP_NAME = 1
    NAME = 2
    DESCRIPTION = 3
    TYPE = 4
    UNIT = 5
    SIZE = 6
    CAP = 7
    CONSTRAINTS = 8


class DevParams(IntEnum):
    """Sane device parameters."""

    FORMAT = 0
    LAST_FRAME = 1
    RESOLUTION = 2
    DEPTH = 3
    BYTES_PER_LINE = 4


class DevStatus(IntEnum):
    """Sane device statuses."""

    IDLE = 0
    SCANNING = 1
    COMPLETED = 2
    ERROR = 3


class JobStatus(IntEnum):
    """Sane job statuses."""

    STARTED = 0
    COMPLETED = 1
    ERROR = 2


class DesanityDevice():
    """Wrapper for a SANE device."""

    _sane_device = None
    _status = DevStatus.IDLE
    _max_saved_jobs = 10
    _jobs = []
    _current_job = None

    def __init__(self, sane_device, max_saved_jobs=10):
        """Initialize a DesanityDevice."""
        self._sane_device = sane_device
        self._max_saved_jobs = max_saved_jobs

    @property
    def sane_device(self):
        """Return the SANE device."""
        return self._sane_device

    @property
    def status(self):
        """Return the status of the device."""
        return self._status

    @property
    def parameters(self):
        """Return the SANE device properties."""
        parameters = self._sane_device.get_parameters()

        return {
            'format': parameters[DevParams.FORMAT],
            'last_frame': parameters[DevParams.LAST_FRAME],
            'pixelPerLine': parameters[DevParams.RESOLUTION][0],
            'lines': parameters[DevParams.RESOLUTION][1],
            'depth': parameters[DevParams.DEPTH],
            'bytes_per_line': parameters[DevParams.BYTES_PER_LINE]
        }

    @property
    def options(self):
        """Return the options available for the device."""
        # parse the option tuples
        options = self._sane_device.get_options()
        ret = []
        for opt in options:
            # parse the constraints option
            constraints = self._parse_constraints(
                opt[DevOptions.CONSTRAINTS])

            # parse the property name and value
            prop_name, prop_value = self._parse_name_value(
                opt[DevOptions.PROP_NAME])

            ret.append({
                'propertyName': prop_name,
                'Name': opt[DevOptions.NAME],
                'Description': opt[DevOptions.DESCRIPTION],
                'type': opt[DevOptions.TYPE],
                'unit': opt[DevOptions.UNIT],
                'size': opt[DevOptions.SIZE],
                'cap': opt[DevOptions.CAP],
                'constraints': constraints,
                'value': prop_value
            })

        return ret

    @property
    def jobs(self):
        """Return the list of running and completed jobs on the device."""
        return self._jobs

    def set_option(self, option_name, value):
        """Set a SANE device option."""
        keys = list(map(lambda opt: opt["propertyName"], self.options))
        if option_name not in keys:
            raise DesanityUnknownOption(f"Option {option_name} not found for"
                                        "device {device_name}")

        try:
            setattr(self._sane_device, option_name, value)
        except SaneException as ex:
            raise DesanityOptionInvalidValue() from ex

    def scan(self):
        """Use the SANE device to perform a scan."""
        if self.status not in (DevStatus.IDLE, DevStatus.COMPLETED):
            raise DesanityDeviceBusy()

        job = self._get_next_job()

        Thread(target=self._start_scan, args=(job,)).start()

        return job

    def _start_scan(self, job):
        """Private method to begin a scan asyncronously."""
        try:
            self._status = DevStatus.SCANNING
            pages = self._sane_device.multi_scan()
            for page in pages:
                job.add_image(page)
        except Exception as ex:
            job.mark_error(str(ex))
            raise ex
        finally:
            self._status = DevStatus.COMPLETED
            job.mark_complete()

    def _get_next_job(self):
        """Return the next available job number for the device."""
        if len(self._jobs) == self._max_saved_jobs:
            self._jobs.pop()

        new_job = DesanityJob(int(datetime.timestamp(datetime.now())))

        self._jobs.insert(0, new_job)
        self._current_job = new_job

        return self._current_job

    def _parse_constraints(self, opt):
        """Return the constraits for the given option."""
        if opt is None:
            constraints = None
        elif isinstance(opt, tuple):
            constraints = {
                'min': opt[0],
                'max': opt[1],
                'step': opt[2]
            }
        elif isinstance(opt, list):
            constraints = opt
        else:
            constraints = None

        return constraints

    def _parse_name_value(self, opt):
        """Parse the property name and value from the option."""
        if opt is not None:
            property_name = opt.replace('-', '_')

            if self._sane_device[property_name].is_active():
                value = repr(getattr(self._sane_device, property_name))
            else:
                value = None
        else:
            property_name = None
            value = None

        return property_name, value


class DesanityJob():
    """A Scanning job."""

    _job_number = None
    _images = []
    _start_date = None
    _end_date = None
    _job_status = None
    _error_str = None

    def __init__(self, job_number):
        """Initiatlize the Job."""
        self._job_number = job_number
        self._start_date = datetime.now()
        self._job_status = JobStatus.STARTED

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
# }}}
