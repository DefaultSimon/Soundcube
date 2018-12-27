# coding=utf-8
from quart import Quart

app = Quart(__name__)

# Load the default config and overwrite with custom one (if provided)
app.config.from_pyfile("soundcube/quartconfig_defaults.ini")
app.config.from_pyfile("data/quartconfig.ini", silent=True)

# IMPORT BLUEPRINTS
from soundcube.api.ping import app as bp_ping

app.register_blueprint(bp_ping)

# Run with `run.bat` (or `hypercorn server:app`)
