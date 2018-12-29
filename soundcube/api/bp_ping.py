# coding=utf-8
########################
# Ping/Other Blueprint
#
# Full route of this blueprint: /
########################
from quart import Blueprint

from soundcube.api.web_utilities import jsonify_response

app = Blueprint("ping", __name__)


@app.route("/ping")
async def ping():
    return jsonify_response({"pong": "ok"})
