import settings

__version__ = "0.1"
__all__ = ["api", "vlan", "host", "query"]

from .decorators import BanchiFlask
from flask.ext.sqlalchemy import SQLAlchemy

app = BanchiFlask(__name__)
app.version = __version__
db = SQLAlchemy()


def setup():
    app.debug = settings.DEBUG
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URI

    db.init_app(app)

    return app

from importlib import import_module
map(lambda module: import_module("." + module, __name__), __all__)
