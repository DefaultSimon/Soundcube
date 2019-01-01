# coding=utf-8
########################
# Player Blueprint
#
# Full route of this blueprint: /music/player/
########################
import re
import logging
from quart import Blueprint, request, abort

from .web_utilities import with_status, get_json_from_request, process_time
from ._bp_types import StatusType

from ..core.player import Player
from ..core.exceptions import MediaNotLoaded, QueueException, PlayerException, \
                              YoutubeException, OutsideTimeBounds

app = Blueprint("player", __name__)
player = Player()

# OTHER

log = logging.getLogger(__name__)
# regex: hh:mm:ss[.ms]
time_regex = re.compile(r"([0-9]+:?){1,3}(\.[0-9]+)?")


@app.route("/quickQueue", methods=["POST"])
async def player_queue():
    """
    Full route: /music/player/quickQueue

    Request (JSON):
        song: string
        type: Types.PlayType

    Queue a song to play (at the end of the queue or next).
    """
    json = await get_json_from_request(request)

    url = json.get("song")
    if not url:
        return with_status({"message": "Missing 'song' field"}, 400, StatusType.BAD_REQUEST)

    try:
        await player.queue(url)
    except YoutubeException:
        return with_status(None, 400, StatusType.ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


@app.route("/play", methods=["POST"])
async def player_play():
    """
    Full route: /music/player/queue

    Request (JSON): None

    Play the current song.
    """
    # no json expected

    try:
        await player.play()
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    except PlayerException:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


@app.route("/pause", methods=["POST"])
async def player_pause():
    """
    Full route: /music/player/pause

    Request (JSON): None

    Pause the current song.
    """
    # no json expected
    did_pause = await player.pause()

    if did_pause:
        return with_status(None, 200, StatusType.OK)
    else:
        return with_status(None, 440, StatusType.NOOP)


@app.route("/resume", methods=["POST"])
async def player_resume():
    """
    Full route: /music/player/resume

    Request (JSON): None

    Resume the current song.
    """
    # no json expected
    try:
        did_resume = await player.resume()
    except MediaNotLoaded:
        return with_status(None, 441, StatusType.ERROR)
    else:
        if did_resume:
            return with_status(None, 200, StatusType.OK)
        else:
            return with_status(None, 440, StatusType.NOOP)


@app.route("/stop", methods=["POST"])
async def player_stop():
    """
    Full route: /music/player/resume

    Request (JSON): None

    Stop (unload) the current song.
    """
    # no json expected

    was_playing = await player.stop()

    if was_playing:
        return with_status(None, 200, StatusType.OK)
    else:
        return with_status(None, 440, StatusType.NOOP)


@app.route("/next", methods=["POST"])
async def player_next():
    """
    Full route: /music/player/next

    Request (JSON): None

    Play the next song in queue.
    """
    # no json expected

    try:
        await player.next()
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    except PlayerException:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


@app.route("/previous", methods=["POST"])
async def player_previous():
    """
    Full route: /music/player/previous

    Request (JSON): None

    Play the previous song in queue.
    """
    # no json expected

    try:
        await player.previous()
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    except PlayerException:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


@app.route("/setTime", methods=["PATCH"])
async def player_set_time():
    """
    Full route /music/player/setTime

    Request (JSON):
        time: str (format: hh:mm:ss[:ms])

    Move to the required time in the song.
    """
    json = await get_json_from_request(request)

    audio_time = json.get("time")
    if not audio_time:
        return with_status({"message": "Missing 'time' field"}, 400, StatusType.BAD_REQUEST)

    # Make sure that time is in the correct format
    if re.match(time_regex, audio_time) is None:
        return with_status({"message": "Malformed 'time' field"}, 400, StatusType.BAD_REQUEST)

    try:
        time_in_float = process_time(audio_time)
    except TypeError:
        return with_status({"message": "Invalid 'time' format"}, 400, StatusType.BAD_REQUEST)

    try:
        log.debug(f"Parsed time: {time_in_float}")
        did_change = await player.set_time(time_in_float)
    except RuntimeError:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    except OutsideTimeBounds:
        return with_status(None, 441, StatusType.ERROR)
    else:
        if did_change:
            return with_status(None, 200, StatusType.OK)
        else:
            return with_status(None, 440, StatusType.NOOP)
