from . import app
from .decorators import datatype
import httplib


@app.get('/')
@datatype
def index():
    return app.endpoints, httplib.OK


@app.get('/version/')
@datatype
def get_version():
    return app.__version__
