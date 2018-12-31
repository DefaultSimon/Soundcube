# coding=utf-8
########################
# Player Blueprint
#
# Full route of this blueprint: /music/player/
########################
from quart import Blueprint, request, abort

from soundcube.api.web_utilities import with_status, get_json_from_request

from ..core.player import Player
from ..core.exceptions import MediaNotLoaded, QueueException, PlayerException
from ._bp_types import StatusType

app = Blueprint("player", __name__)
player = Player()


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
        return abort(400)

    await player.queue(url)

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
