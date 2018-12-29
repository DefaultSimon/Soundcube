# coding=utf-8
import pafy
import logging
from ..config import DEV_KEY

log = logging.getLogger(__name__)

pafy.set_api_key(DEV_KEY)


def get_pafy(url: str):
    log.debug(f"Creating new Pafy object for {url}")
    video = pafy.new(url, basic=True)

    log.info(f"Fetched new video: {video.title}")

    return video


def get_audio_url(url: str = None, pafy_: pafy.pafy.Pafy = None):
    if url:
        pf = get_pafy(url)
    else:
        pf = pafy_

    return pf.getbestaudio(ftypestrict=False).url
