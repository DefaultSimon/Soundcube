# coding=utf-8
########################
# Ping/Other Blueprint
#
# Full route of this blueprint: /
########################
import os
import logging
from quart import Blueprint, send_from_directory

from ..config import PUBLIC_URL, PORT, FRONTEND_BUILD_LOCATION

STATIC_FOLDER = os.path.join(FRONTEND_BUILD_LOCATION, "static")
TEMPLATE_FOLDER = FRONTEND_BUILD_LOCATION

INDEX_HTML = os.path.join(FRONTEND_BUILD_LOCATION, "index.html")
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
        with open(INDEX_HTML) as f:
            page = f.read().replace("{{soundcube_host}}", str(PUBLIC_URL))
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
