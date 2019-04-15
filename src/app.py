
from flask import Flask
from .api import ApiResult, api
from .storage import InMemoryBackend, FileSystemBackend
from .doc import auto, doc


class Api(Flask):
    """Flask subclass using the custom make_response"""

    def make_response(self, rv):
        if isinstance(rv, ApiResult):
            return rv.to_response()
        else:
            return super().make_response(rv)


def create_app(config='src.config.Development'):
    app = Api(__name__)
    app.config.from_object(config)
    auto.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(doc)

    # app.storage = FileSystemBackend("/tmp")
    app.storage = InMemoryBackend()
    return app



