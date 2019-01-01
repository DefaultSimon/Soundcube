# coding=utf-8
########################
# Queue Blueprint
#
# Full route of this blueprint: /music/queue
########################
import logging
from typing import List
from quart import Blueprint, request

from .web_utilities import with_status, get_json_from_request
from ._bp_types import StatusType, PlayType

from ..core.player import Player
from ..core.youtube import YoutubeAudio
from ..core.exceptions import YoutubeException

log = logging.getLogger(__name__)
app = Blueprint("queue", __name__)
player = Player()


# noinspection PyPep8Naming
def dictify_YoutubeAudio(obj: YoutubeAudio) -> dict:
    return {
        "video_id": obj.videoid,
        "title": obj.title,
        "length": obj.length,
        "username": obj.pafy.username,
        "published": obj.pafy.published,
        "viewcount": obj.pafy.viewcount
    }


def get_friendly_queue() -> list:
    """
    Returns a JSON-friendly representation of the queue
    :return: list
    """
    queue: List[YoutubeAudio] = player._queue.queue

    return [dictify_YoutubeAudio(a) for a in queue]


@app.route("/get")
async def queue_get():
    """
    Full route: /music/queue/get

    Returns the current queue
    """
    # no json expected

    payload = {
        "queue": get_friendly_queue()
    }

    return with_status(payload, 200, StatusType.OK)


@app.route("/add", methods=["POST"])
async def queue_add():
    """
    Full route: /music/queue/get

    Request (JSON):
        song: video_id
        position: int

    Adds a song to the queue.
    """
    json = await get_json_from_request(request)

    song, position = json.get("song"), json.get("position")
    if not song or not position:
        return with_status({"message": "Missing fields"}, 400, StatusType.BAD_REQUEST)
    try:
        position = int(position)
    except ValueError:
        return with_status({"message": "Invalid 'position'"}, 400, StatusType.BAD_REQUEST)

    try:
        await player.queue(song, PlayType.AT_POSITION, position)
    except YoutubeException:
        return with_status(None, 400, StatusType.ERROR)
    else:
        payload = {
            "new_queue": get_friendly_queue()
        }

        return with_status(payload, 200, StatusType.OK)
