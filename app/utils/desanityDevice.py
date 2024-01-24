###############################################################################
#  DesanityDevice.py for the desanity microservice                            #
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
import uuid
import sane
from .desanityExceptions import DesanityDeviceBusy, DesanityDeviceNotEnabled
from .desanityExceptions import DesanityUnknownOption, SaneException
from .desanityExceptions import DesanitySaneException
from .desanityJobs import DesanityJob
# }}}

# desanity device {{{


class DevParams(IntEnum):
    """Sane device parameters."""

    FORMAT = 0
    LAST_FRAME = 1
    RESOLUTION = 2
    DEPTH = 3
    BYTES_PER_LINE = 4


class DevStatus(IntEnum):
    """Sane device statuses."""

    DISABLED = 0
    ENABLED = 1
    SCANNING = 2
    COMPLETED = 3
    ERROR = 4


class DesanityDevice():
    """Wrapper for a SANE device."""

    _name = None
    _vendor = None
    _model = None
    _device_type = None
    _guid = None
    _options = {}
    _sane_device = None
    _status = DevStatus.DISABLED
    _jobs = []
    _current_job = None

    def __init__(self, name, vendor, model, device_type):
        """Initialize a DesanityDevice."""
        self._guid = str(uuid.uuid4())
        self._name = name
        self._vendor = vendor
        self._model = model
        self._device_type = device_type

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def vendor(self):
        """Return the vendor of the device."""
        return self._vendor

    @property
    def model(self):
        """Return the model of the device."""
        return self._model

    @property
    def device_type(self):
        """Return the type of the device."""
        return self._device_type

    @property
    def guid(self):
        """Return the guid of the device."""
        return self._guid

    @property
    def status(self):
        """Return the device status."""
        return self._status

    @property
    def enabled(self):
        """Return whether the device is opened."""
        return self._sane_device is not None

    @property
    def sane_device(self):
        """Return the SANE device."""
        return self._sane_device

    @property
    def parameters(self):
        """Return the SANE device properties."""
        if self._sane_device is None:
            raise DesanityDeviceNotEnabled()

        try:
            parameters = self._sane_device.get_parameters()
        except SaneException as ex:
            raise DesanitySaneException() from ex

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
        if self._sane_device is None:
            raise DesanityDeviceNotEnabled()

        # parse the option tuples
        options = list(self._sane_device.opt.keys())

        for opt in options:
            if opt == '':
                continue

            self._parse_option(opt)

        return self._options

    @property
    def jobs(self):
        """Return the list of running and completed jobs on the device."""
        return self._jobs

    def enable(self):
        """Open the sane device."""
        try:
            self._sane_device = sane.open(self.name)
            self._status = DevStatus.ENABLED
        except SaneException as ex:
            raise DesanitySaneException(str(ex)) from ex

    def disable(self):
        """Close the sane device."""
        self._sane_device.close()
        self._options = {}
        self._status = DevStatus.DISABLED
        self._sane_device = None

    def set_option(self, option_name, value):
        """Set a SANE device option."""
        if self._sane_device is None:
            return

        keys = list(self.options)
        if option_name not in keys:
            raise DesanityUnknownOption(f"Option {option_name} not found for"
                                        "device {device_name}")

        try:
            setattr(self._sane_device, option_name, value)
        except SaneException as ex:
            raise DesanitySaneException from ex

    def scan(self):
        """Use the SANE device to perform a scan."""
        if self._sane_device is None:
            return None

        if self.status not in (DevStatus.ENABLED, DevStatus.COMPLETED):
            raise DesanityDeviceBusy()

        job = self._get_next_job()

        Thread(target=self._start_scan, args=(job,)).start()

        return job

    def serialize_json(self):
        """Return the device as a json object."""
        return {
                'name': self.name,
                'vendor': self.vendor,
                'model': self.model,
                'device_type': self.device_type,
                'guid': self.guid,
            }

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
        # if len(self._jobs) == self._max_saved_jobs:
        #     self._jobs.pop()

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

    def _parse_option(self, opt_name):
        """Parse device option."""
        if opt_name == '':
            return

        opt = self._sane_device[opt_name]

        if not opt.is_active():
            return

        self._options[opt_name] = {}
        self._options[opt_name]['name'] = opt.name
        self._options[opt_name]['value'] = getattr(self._sane_device,
                                                   opt_name)
        self._options[opt_name]['py_name'] = opt.py_name
        self._options[opt_name]['type'] = opt.type
        self._options[opt_name]['unit'] = opt.unit
        self._options[opt_name]['size'] = opt.size
        self._options[opt_name]['desc'] = opt.desc
        constraints = self._parse_constraints(opt.constraint)
        self._options[opt_name]['constraints'] = constraints

    def _parse_name_value(self, opt):
        """Parse the property name and value from the option."""
        if opt is not None and not opt == "":
            property_name = opt.replace('-', '_')

            if self._sane_device[property_name].is_active():
                value = repr(getattr(self._sane_device, property_name))
            else:
                value = None
        else:
            property_name = None
            value = None

        return property_name, value
# }}}
