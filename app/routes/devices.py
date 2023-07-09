###############################################################################
#  devices.py for archivist descry microservices                              #
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

# Module DocuString ## {{{
"""Routes to interact with scanning devices."""
# }}}

# libraries # {{{
import base64
from io import BytesIO
from flask import Blueprint, request
from app.utils import desanity, DesanityUnknownDev, DesanityException
from app.utils import JobStatus, DesanityDeviceBusy
# }}}

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


@devices_bp.route('', methods=['GET'])
def get_devices():
    """
    Retrieve a list of available devices from the sane.

    ---
    tags:
      - devices
    responses:
      200:
        description: A list of devices
      500:
        description: Error occured while getting a list of available devices
    """
    req = None if not request.is_json else request.get_json()
    no_cache = False

    if req is not None and req.has_key('no_cache'):
        no_cache = bool(req['no_cache'])

    # try to get the devices throw a internal server error if it fails
    try:
        if no_cache:
            devices = desanity.available_devices
        else:
            devices = desanity.refresh_devices()

    except DesanityException as ex:
        return {
            'ErrMsg': f"An error occured while getting devices: {ex}"
        }, 500

    # return the devices returned by desanity
    return {
        'devices': devices
    }, 200


@devices_bp.route('/open', methods=['POST'])
def open_device():
    """
    Open a SANE device within Descry.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        in: body
        description: Name of device to open
        required: true
        type: string
    responses:
      201:
         description: Device is opened
      404:
         description: Device not found
    """
    try:
        data = request.get_json()
        device_name = data['device_name']

        device_id = desanity.open_device(device_name)
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404

    return {
        'device_id': device_id
    }, 201


@devices_bp.route('/open/<string:device_name>', methods=['GET'])
def get_open_device(device_name):
    """
    Get a scanning device information.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        in: path
        description: Name of device to open
        required: true
        type: string
    responses:
      200:
         description: Device description, options and parameters
      404:
         description: Device not found

    """
    try:
        if device_name not in desanity.open_devices():
            raise DesanityUnknownDev

        device = desanity.get_open_device(device_name)

        params = device.parameters
        opts = device.options

    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404

    return {
        "device_name": device_name,
        "options": opts,
        "parameters": params
    }, 200


@devices_bp.route('/<string:device_name>/scan', methods=['GET'])
def scan(device_name):
    """
    Scan a document using device_name.

    ---
    tags:
      - devices
    parameters:
      - name: device_name
        id: path
        description: id of the device to scan with
        required: true
        type: string
    responses:
      202:
        description: Return the job resource handler for the scanning job
      404:
        description: Device not found
      503:
        description: Device is busy
    """
    try:
        if device_name not in desanity.open_devices():
            raise DesanityUnknownDev

        device = desanity.get_open_device(device_name)
        job = device.scan()
    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found or not opened'
        }, 404
    except DesanityDeviceBusy:
        return {
            "ErrMsg": f"Sane device {device_name} is busy"
        }, 503

    return {
        'jobId': job.job_number,
        'job_url': job_url(device_name, job.job_number)
    }, 202


@devices_bp.route('<string:device_name>/jobs', methods=['GET'])
def get_jobs(device_name):
    """
    Get list running or completed job for the given device.

    ---
    tags:
      - jobs
    parameters:
    - name: device_name
      in: path
      description: Device common name
      required: true
      type: string
    response:
      200:
        description: List of jobs, including job id, status, and start,end date
      404:
        description: Device not found
    """
    try:
        if device_name not in desanity.open_devices():
            raise DesanityUnknownDev

        device = desanity.get_open_device(device_name)

        jobs_info = list(map(lambda job: {
            "id": job.job_number,
            "status": job.status,
            "pageCount": len(job.images),
            "startDate": job.start_date,
            "endDate": job.end_date}, device.jobs))

    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404

    return jobs_info, 200


@devices_bp.route('<string:device_name>/jobs/<int:job_number>',
                  methods=['GET'])
def get_job(device_name, job_number):
    """
    Get a running or completed job on a given device by job number.

    ---
    tags:
      - jobs
    parameters:
    - name: device_name
      in: path
      description: Device common name
      required: true
      type: string
    - name: job_number
      in: path
      description: Job number
      required: true
      type: integer
    response:
      200:
        description: Job information, including status and images
      404:
        description: Job or device not found
    """
    try:
        if device_name not in desanity.open_devices():
            raise DesanityUnknownDev

        device = desanity.get_open_device(device_name)

        jobs = device.jobs
        if job_number not in list(map(lambda job: job.job_number, jobs)):
            return {
                'ErrMsg': f'Job {job_number} was not found'
            }

        job = next(job for job in jobs if job.job_number == job_number)

    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404
    except StopIteration:
        return {
            'ErrMsg': f'Job {job_number} was not found'
        }

    ret = {
        "id": job_number,
        "pageCount": len(job.images),
        "pages": list(map(image2base64str, job.images)),
        "status": job.status,
        "startDate": job.start_date
        }

    if job.status == JobStatus.ERROR:
        ret["errorMessage"] = job.error_str

    if job.status == JobStatus.COMPLETED:
        ret["endDate"] = job.end_date

    return ret, 200


# pylint: disable=line-too-long
@devices_bp.route('<string:device_name>/jobs/<int:job_number>/page/<int:page_number>', methods=['GET']) # noqa
def get_page(device_name, job_number, page_number):
    """
    Return a scanned page from a scan job.

    ---
    tags:
      - jobs
    parameters:
    - name: device_name
      in: path
      description: Device common name
      required: true
      type: string
    - name: job_number
      in: path
      description: Job number
      required: true
      type: integer
    - name: page_number
      in: path
      description: Page number (1s indexed)
      required: true
      type: integer
    - name: format
      in: body
      description: Image format of the page
      required: false
      type: string
      default: JPEG
    response:
      200:
        description: Job information, including status and images
      404:
        description: Job or device not found
    """
    try:
        if device_name not in desanity.open_devices():
            raise DesanityUnknownDev

        device = desanity.get_open_device(device_name)

        jobs = device.jobs
        if job_number not in list(map(lambda job: job.job_number, jobs)):
            return {
                'ErrMsg': f'Job {job_number} was not found'
            }

        job = next(job for job in jobs if job.job_number == job_number)

        if page_number > len(job.images) or page_number < 1:
            return {
                'ErrMsg': f'Page number {page_number} does not exist'
            }, 404

    except DesanityUnknownDev:
        return {
            'ErrMsg': f'Sane device {device_name} not found'
        }, 404
    except StopIteration:
        return {
            'ErrMsg': f'Job {job_number} was not found'
        }

    ret = {
        "id": "job",
        "pageNumber": page_number,
        "page": image2base64str(job.images[page_number-1])
        }

    return ret, 200


def image2base64str(image, fmt="JPEG"):
    """Return a base64 string of an PIL Image."""
    buf = BytesIO()
    image.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def job_url(device_name, job_number):
    """Return a job url."""
    return f"{request.url_root}devices/{device_name}/jobs/{job_number}"
