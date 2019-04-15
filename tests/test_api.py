import unittest
import pathlib
from io import BytesIO

from src.app import create_app
from src.api import hashfunc

from flask import url_for
from PIL import Image


HERE = pathlib.Path(__file__).parent.absolute()


class TestApi(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.formats = self.app.config["ALLOWED_FORMATS"]
        self.images = [path for path in (HERE / "images").iterdir() if path.suffix.endswith(self.formats)]

    def test_upload(self):

        for path in self.images:
            fh = open(path, "rb")
            digest = hashfunc(fh.read()).hexdigest()
            fh.seek(0)

            data = {'file': fh}
            with self.app.test_request_context():
                url = url_for("api.upload")

            resp = self.client.post(url, data=data, content_type='multipart/form-data')

            self.assertEqual(200, resp.status_code,)
            self.assertEqual(digest, resp.get_json()["id"])

    def test_download(self):
        for path in self.images:

            with open(path, "rb") as fh:
                file = fh.read()

            digest = hashfunc(file).hexdigest()

            self.app.storage.set(f"{digest}{path.suffix}", file)

            with self.app.test_request_context():
                url = url_for("api.get_file", fileid=digest, format=path.suffix.lstrip("."))

            resp = self.client.get(url)

            self.assertEqual(200, resp.status_code)
            self.assertEqual(digest, hashfunc(resp.data).hexdigest())

    def test_conversion(self):
        for path in self.images:
            with open(path, "rb") as fh:
                file = fh.read()

            digest = hashfunc(file).hexdigest()
            self.app.storage.set(f"{digest}{path.suffix}", file)

            filename, extension = path.parts[-1].split(".")
            formats = list(self.formats)
            formats.remove(extension)

            for format in formats:
                with self.app.test_request_context():
                    url = url_for("api.get_file", fileid=digest, format=format)

                resp = self.client.get(url)
                Image.open(BytesIO(resp.data))

                self.assertEqual(200, resp.status_code)


