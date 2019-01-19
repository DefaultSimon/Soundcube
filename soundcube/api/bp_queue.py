# coding=utf-8
########################
# Queue Blueprint
#
# Full route of this blueprint: /music/queue
########################
import logging
from typing import List
from quart import Blueprint, request

from .web_utilities import with_status, get_json_from_request, dictify_YoutubeAudio
from ._bp_types import StatusType, PlayType

from ..core.player import Player
from ..core.youtube import YoutubeAudio
from ..core.exceptions import YoutubeException, QueueException

log = logging.getLogger(__name__)
app = Blueprint("queue", __name__)
player = Player()


def get_json_queue() -> list:
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

    :return: the current queue
    """
    # no json expected

    payload = {
        "queue": get_json_queue(),
        "current_song": player._queue.current_index
    }

    return with_status(payload, 200, StatusType.OK)


@app.route("/add", methods=["POST"])
async def queue_add():
    """
    Full route: /music/queue/get

    Request (JSON):
        song: video_id
        position: int
        set_playing: bool

    Adds a song to the queue.
    :return: The new queue
    """
    json = await get_json_from_request(request)

    song, position = json.get("song"), json.get("position")
    set_playing = bool(json.get("set_playing", False))
    if song is None or position is None:
        return with_status({"message": "Missing fields"}, 400, StatusType.BAD_REQUEST)
    try:
        position = int(position)
    except ValueError:
        return with_status({"message": "Invalid 'position'"}, 400, StatusType.BAD_REQUEST)

    try:
        await player.player_queue(song, PlayType.AT_POSITION, position=position, set_playing=set_playing)
    except YoutubeException:
        return with_status(None, 441, StatusType.ERROR)
    else:
        data = {
            "new_queue": get_json_queue()
        }

        return with_status(data, 200, StatusType.OK)


@app.route("/remove", methods=["POST"])
async def queue_remove():
    """
    Full route: /music/queue/remove

    Request (JSON):
        position: int

    Remove a song from the queue
    :return: the new queue
    """
    json = await get_json_from_request(request)

    position = json.get("position")
    if position is None:
        return with_status({"message": "Missing 'position' field"}, 400, StatusType.BAD_REQUEST)
    if type(position) is not int:
        return with_status({"message": "'position' field should be an integer"}, 400, StatusType.BAD_REQUEST)

    try:
        await player.queue_remove(position)
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    else:
        data = {
            "new_queue": get_json_queue()
        }

        return with_status(data, 200, StatusType.OK)


@app.route("/move", methods=["POST"])
async def queue_move():
    """
    Full route: /music/queue/move

    Request (JSON):
        current_index: int
        new_index: int

    Move a song to a position in the queue
    :return: the new queue
    """
    json = await get_json_from_request(request)

    current, new = json.get("current_index"), json.get("new_index")
    # Can't do 'not current' because that includes 0
    if current is None or new is None:
        return with_status({"message": "One or more fields missing: 'current', 'new'"}, 400, StatusType.BAD_REQUEST)

    if type(current) is not int:
        return with_status({"message": "'current_index' field should be an integer"}, 400, StatusType.BAD_REQUEST)
    if type(new) is not int:
        return with_status({"message": "'new_index' field should be an integer"}, 400, StatusType.BAD_REQUEST)

    try:
        # Explanation of 'new + 1':
        # This makes sure that the song is inserted AFTER new_index
        if current < new:
            new += 1

        await player.queue_move(current, new)
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    else:
        new_queue = get_json_queue()
        log.debug(f"New queue: {','.join([repr(a) for a in new_queue])}")

        data = {
            "new_queue": new_queue
        }

        return with_status(data, 200, StatusType.OK)
