
from flask import Blueprint
from flask_selfdoc import Autodoc


doc = Blueprint('doc', __name__, url_prefix='/doc')
auto = Autodoc()


@doc.route('/')
def documentation():
    return auto.html(title='Api Documentation')


