from PIL import Image
from io import BytesIO


def convert_image(file, filetype):
    if filetype.lower() == "jpg":
        filetype = "jpeg"
    img = Image.open(file)
    img = img.convert("RGB")

    bytestream = BytesIO()
    img.save(bytestream, filetype)
    bytestream.seek(0)

    return bytestream


def validate_image(file, valid_formats):
    try:
        img = Image.open(file)
    except IOError:
        return False
    return img.format in map(str.upper, valid_formats)


