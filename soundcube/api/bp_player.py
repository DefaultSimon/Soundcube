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
async def ping():
    """
    Full route: /music/player/play/

    Request (JSON):
        song: string
        type: Types.PlayType

    Add a song to play (immediately or after the current song)
    :return: None
    """
    json = await get_json_from_request(request)

    url = json.get("song")
    if not url:
        return abort(400)

    await player.play(url)

    return with_status(None, 200, StatusType.OK)
