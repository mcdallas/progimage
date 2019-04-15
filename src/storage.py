import logging
import tempfile
import pathlib
# from functools import lru_cache

logger = logging.getLogger(__name__)


class StorageBackend:

    def set(self, key, data):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError


class FileSystemBackend(StorageBackend):

    def __init__(self, path=None):
        path = path or tempfile.gettempdir()
        self.dir = pathlib.Path(path)
        print(f"Using {self.dir.absolute()} to store images")

    def set(self, key, data):
        try:
            with open(self.dir / key, "wb") as fh:
                fh.write(data)
            return True
        except OSError as e:
            logger.exception(e)
            return False

    # @lru_cache(maxsize=100)
    def get(self, key):
        try:
            logger.info(f"Looking for: {self.dir / key}")
            with open(self.dir / key, "rb") as fh:

                return fh.read()
        except OSError:
            return None

    def delete(self, key):
        raise NotImplementedError


class InMemoryBackend(StorageBackend):

    def __init__(self):
        self.data = {}

    def set(self, key, data):
        self.data[key] = data
        return True

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        try:
            del self.data[key]
        except KeyError:
            return False
        return True


