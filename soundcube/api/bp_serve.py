# coding=utf-8
########################
# Ping/Other Blueprint
#
# Full route of this blueprint: /
########################
import os
import logging
from quart import Blueprint, send_from_directory

from ..config import HOST, PORT

BP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.normpath(os.path.join(BP_DIR, "../../react/build/static"))
TEMPLATE_FOLDER = os.path.normpath(os.path.join(BP_DIR, "../../react/build"))

JS_FOLDER = os.path.join(STATIC_FOLDER, "js")
CSS_FOLDER = os.path.join(STATIC_FOLDER, "css")

log = logging.getLogger(__name__)
app = Blueprint("serve", __name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def index(path):
    """
    Serves files from the react/build/static directory.
    """
    if path == "":
        # So we don't have to deal with templating stuff
        with open("react/build/index.html") as f:
            page = f.read().replace("{{soundcube_host}}", str(HOST))
            page = page.replace("{{soundcube_port}}", str(PORT))

            return page
    else:
        return await send_from_directory(TEMPLATE_FOLDER, path)


@app.route("/static/js/<path:path>")
async def serve_static(path):
    """
    Specifically serves files from the react/build/static/js directory.
    """
    return await send_from_directory(JS_FOLDER, path)


@app.route("/static/css/<path:path>")
async def serve_static_css(path):
    """
    Specifically serves files from the react/build/static/css directory.
    """
    return await send_from_directory(CSS_FOLDER, path)
