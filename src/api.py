import os
from io import BytesIO
from hashlib import sha256 as hashfunc
from flask import make_response, jsonify, Blueprint, request, current_app, send_file

from .image import convert_image, validate_image
from .doc import auto

api = Blueprint('api', __name__, url_prefix='/api')


class ApiResult:
    """A wrapper for the json object of an api result. Provides consistency across endpoints"""
    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self):
        return make_response(jsonify(self.value), self.status)


class ApiException(Exception):
    """This exception should be raised by all api endpoints. It will be caught by the error
    handler and a standardized response will be returned"""
    def __init__(self, message, status=400):
        self.message = message
        self.status = status

    def to_result(self):
        return ApiResult({'error': self.message}, status=self.status)


api.register_error_handler(ApiException, lambda err: err.to_result())


def lookup_image(uniqueid, extension):
    """Retrieves an image by id, returns it if it has the correct extension or otherwise converts it"""
    for ext in current_app.config["ALLOWED_FORMATS"]:
        key = f"{uniqueid}.{ext}"
        image = current_app.storage.get(key)
        if image:
            if ext == extension:
                return BytesIO(image)
            return convert_image(BytesIO(image), extension)
    return None


@api.route('/upload', methods=['POST'])
@auto.doc(args=["file"])
def upload():
    """Receives an image, assigns a unique id and stores it"""

    if 'file' not in request.files:
        raise ApiException('Expected file upload', 422)

    filestream = request.files['file']
    name, extension = os.path.splitext(filestream.filename)
    extension = extension.lstrip(".")
    name = name.strip()
    maxlen = current_app.config['MAXIMUM_FILENAME_LENGTH']
    formats = current_app.config["ALLOWED_FORMATS"]

    if len(name) > maxlen:
        raise ApiException(f'Maximum filename length is {maxlen} characters', 400)

    if extension not in formats:
        raise ApiException(f'Unsupported extension {extension}. Expected one of {formats}', 422)

    if not validate_image(filestream, valid_formats=formats):
        raise ApiException(f"Unsupported file type", 422)

    filestream.seek(0)
    file = filestream.read()
    digest = hashfunc(file).hexdigest()
    key = f"{digest}.{extension}"
    success = current_app.storage.set(key, file)

    if success:
        return ApiResult({"id": digest})
    raise ApiException("Error saving file", 500)


@api.route('/image/<fileid>')
@auto.doc(args=["format"], defaults={"format": "png"})
def get_file(fileid):
    """Returns an image with the given format"""
    extension = request.args.get('format', 'png').lower()
    if extension not in current_app.config["ALLOWED_FORMATS"]:
        raise ApiException("File type not supported")

    image = lookup_image(fileid, extension)

    if not image:
        raise ApiException("Not found", 404)

    return send_file(image, mimetype=f"image/{extension}")







