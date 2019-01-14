# coding=utf-8
########################
# Player Blueprint
#
# Full route of this blueprint: /music/player/
########################
import re
import logging
from quart import Blueprint, request

from .web_utilities import with_status, get_json_from_request, process_time, dictify_YoutubeAudio
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
async def player_quick_queue():
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
        await player.player_queue(url)
    except YoutubeException:
        return with_status(None, 400, StatusType.ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


@app.route("/getCurrentSong")
async def player_get_current():
    """
    Full route: /music/player/getCurrentSong

    Request (JSON): None

    :return: info about the current song.
    """
    current_song = player._queue.current_audio

    if current_song is None:
        return with_status(None, 440, StatusType.NOOP)
    else:
        is_playing = player.player_is_playing()

        data = {
            "current_song": dictify_YoutubeAudio(current_song),
            "is_playing": is_playing,
            "time": player.player_get_time() if is_playing else None
        }

        return with_status(data, 200, StatusType.OK)


@app.route("/play", methods=["POST"])
async def player_play():
    """
    Full route: /music/player/queue

    Request (JSON): None

    Play the current song.
    """
    # no json expected

    try:
        await player.player_play()
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
    did_pause = await player.player_pause()

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
        did_resume = await player.player_resume()
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

    was_playing = await player.player_stop()

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
        await player.player_next()
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
        await player.player_previous()
    except QueueException:
        return with_status(None, 441, StatusType.ERROR)
    except PlayerException:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    else:
        return with_status(None, 200, StatusType.OK)


async def player_get_time():
    # Return a 441 if no song is loaded
    if not player.player_is_song_loaded():
        return with_status(None, 441, StatusType.ERROR)

    # Otherwise, return the data
    data = {
        "time": await player.player_get_time() or 0,
        "total_length": player._queue.current_audio.length
    }

    return with_status(data, 200, StatusType.OK)


async def player_set_time():
    json = await get_json_from_request(request)

    audio_time = json.get("time")
    if not audio_time:
        return with_status({"message": "Missing 'time' field"}, 400, StatusType.BAD_REQUEST)

    try:
        time_in_float = int(audio_time)
    except TypeError:
        return with_status({"message": "Invalid 'time' format"}, 400, StatusType.BAD_REQUEST)

    try:
        log.debug(f"Parsed time: {time_in_float}")
        did_change = await player.player_set_time(time_in_float)
    except RuntimeError:
        return with_status(None, 444, StatusType.INTERNAL_ERROR)
    except OutsideTimeBounds:
        return with_status(None, 441, StatusType.ERROR)
    else:
        if did_change:
            return with_status(None, 200, StatusType.OK)
        else:
            return with_status(None, 440, StatusType.NOOP)


@app.route("/audioTime", methods=["GET", "PATCH"])
async def player_audio_time():
    """
    Full route /music/player/audioTime (GET and PATCH)

    GET: Get the current audio time.

    PATCH: Move to the specified time in the song.
    Request (JSON):
        time: integer
    """
    if request.method == "GET":
        return await player_get_time()
    elif request.method == "PATCH":
        return await player_set_time()
    else:
        return with_status(None, 400, StatusType.BAD_REQUEST)
