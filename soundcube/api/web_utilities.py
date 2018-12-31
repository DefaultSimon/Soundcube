# coding=utf-8
from quart.wrappers.response import Response
import logging
from typing import Optional

from ._bp_types import StatusType

log = logging.getLogger(__name__)

try:
    from rapidjson import dumps, loads
except ImportError:
    log.info("'rapidjson' is not available, falling back to built-in json module.")
    from json import dumps, loads


def jsonify_response(json, resp_code=200):
    return Response(dumps(json), resp_code, mimetype="application/json")


def with_status(json: Optional[dict] = None, resp_code: int = 200, status: StatusType = StatusType.OK):
    """
    Creates a response with the provided StatusType and status
    :param json: json to respond with
    :param resp_code: HTTP status code
    :param status: StatusType
    :return: Response to return in the route
    """
    if json is None:
        json = {}

    full_json = {**json, **{"status": status}}

    return jsonify_response(full_json, resp_code)


async def get_json_from_request(response: Response):
    return loads(await response.get_data())
