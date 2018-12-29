# coding=utf-8
import logging
from quart import Quart

log = logging.getLogger(__name__)
app = Quart(__name__)

logging.basicConfig(level=logging.DEBUG)

# Load the default config and overwrite with custom one (if provided)
app.config.from_pyfile("soundcube/quartconfig_defaults.ini")
app.config.from_pyfile("data/quartconfig.ini", silent=True)

# IMPORT BLUEPRINTS
from soundcube.api.bp_ping import app as bp_ping
from soundcube.api.bp_player import app as bp_player

app.register_blueprint(bp_ping)
# app.register_blueprint(bp_queue, url_prefix="/music/queue")
app.register_blueprint(bp_player, url_prefix="/music/player")

# Run with `run.bat` (or `hypercorn server:app`)
