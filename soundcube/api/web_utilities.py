# coding=utf-8
from quart.wrappers.response import Response
from quart.wrappers.request import Request
import logging
from typing import Optional, Union

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


async def get_json_from_request(request: Request):
    return loads(await request.get_data())


def process_time(time_: str) -> Union[int, float]:
    """
    Extracts the full time (in seconds) from a hh:mm:ss[.ms] string
    :param time_: hh:mm:ss[.ms] formatted string
    :return: full time
    """
    # Reverse the parts (so they are in order: seconds, minutes, hours)
    parts = list(reversed(time_.split(":")))

    if len(parts) > 3:
        raise TypeError("invalid format")

    total = 0

    for part, to_seconds in zip(parts, [1, 60, 60 * 60]):
        part = float(part) * to_seconds
        total += part

    return total
