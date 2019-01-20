# coding=utf-8
########################
# Auth Blueprint
#
# Full route of this blueprint: /auth
########################
import logging
from quart import Blueprint

from .web_utilities import with_status
from ._bp_types import StatusType

from ..config import FRONTEND_API_KEY

log = logging.getLogger(__name__)
app = Blueprint("auth", __name__)


@app.route("/youtubeApiKey")
async def ping():
    data = {
        "api_key": FRONTEND_API_KEY
    }

    return with_status(data, 200, StatusType.OK)
