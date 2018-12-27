# coding=utf-8
from quart.wrappers.response import Response
import logging

log = logging.getLogger(__name__)

try:
    from rapidjson import dumps
except ImportError:
    log.info("'rapidjson' is not available, falling back to built-in json module.")
    from json import dumps


def jsonify_response(json, resp_code=200):
    return Response(dumps(json), resp_code, mimetype="application/json")
