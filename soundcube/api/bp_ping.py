# coding=utf-8
########################
# Ping/Other Blueprint
#
# Full route of this blueprint: /
########################
import logging
from quart import Blueprint, request

from soundcube.api.web_utilities import jsonify_response

log = logging.getLogger(__name__)
app = Blueprint("ping", __name__)


@app.route("/ping")
async def ping():
    log.debug(f"Got ping from {request.remote_addr}")
    return jsonify_response({"pong": "ok"})
