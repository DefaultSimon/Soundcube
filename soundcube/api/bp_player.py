# coding=utf-8
########################
# Player Blueprint
#
# Full route of this blueprint: /music/player/
########################
from quart import Blueprint, request, abort

from soundcube.api.web_utilities import with_status, get_json_from_request

from ..core.player import Player
from ._types import StatusType

app = Blueprint("player", __name__)
player = Player()


@app.route("/play", methods=["POST"])
async def player_play():
    """
    Full route: /music/player/play/

    Request (JSON):
        song: string
        type: Types.PlayType

    Add a song to play (immediately or after the current song)
    """
    json = await get_json_from_request(request)

    url = json.get("song")
    if not url:
        return abort(400)

    await player.play(url)

    return with_status(None, 200, StatusType.OK)


@app.route("/pause", methods=["POST"])
async def player_pause():
    """
    Full route: /music/player/pause

    Request (JSON): None

    Pause the current song
    :return:
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

    Resume the current song
    """
    # no json expected
    did_resume = await player.resume()

    if did_resume:
        return with_status(None, 200, StatusType.OK)
    else:
        return with_status(None, 440, StatusType.NOOP)


