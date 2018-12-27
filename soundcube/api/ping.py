# coding=utf-8
from quart import Blueprint

from ..utilities import jsonify_response

app = Blueprint("ping", __name__)


@app.route("/ping")
async def ping():
    return jsonify_response({"pong": "ok"})
