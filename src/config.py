
class Config:
    # Flask
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50mb
    SEND_FILE_MAX_AGE_DEFAULT = 12 * 60 * 60  # 12 hours

    # App
    MAXIMUM_FILENAME_LENGTH = 255
    ALLOWED_FORMATS = ('png', 'jpg', 'jpeg', 'gif', 'bmp')


class Development(Config):
    DEBUG = True
    ENV = 'development'


class Production(Config):
    DEBUG = False
    ENV = 'production'

