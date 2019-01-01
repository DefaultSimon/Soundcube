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
from soundcube.api.bp_queue import app as bp_queue

app.register_blueprint(bp_ping)
app.register_blueprint(bp_queue, url_prefix="/music/queue")
app.register_blueprint(bp_player, url_prefix="/music/player")


# Register a handler to append Access-Control-Allow-Origin headers
@app.after_request
async def handle_headers(response):
    # This header is necessary for clients to be able to receive data from this server
    # see https://stackoverflow.com/questions/10636611/how-does-access-control-allow-origin-header-work
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Run with `run.bat` (or `hypercorn server:app`)
