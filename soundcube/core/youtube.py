# coding=utf-8
import logging

import pafy
from pafy.backend_shared import BasePafy, BaseStream

from ..config import BACKEND_API_KEY
from .exceptions import NoAudioStream
from .utilities import resolve_time, make_random_song_id

log = logging.getLogger(__name__)

pafy.set_api_key(BACKEND_API_KEY)


def get_pafy(url: str) -> BasePafy:
    """
    Parse the YouTube url with pafy.
    :param url: YouTube url
    :return: Pafy object
    """
    log.debug(f"Creating new Pafy object for {url}")
    video = pafy.new(url, basic=True)

    log.info(f"Fetched new video: {video.title}")

    return video


class YoutubeAudio:
    """
    Handles parsing YouTube url via pafy, finds audio streams, ...

    Mostly for use as queue objects.
    """
    __slots__ = ("unique_id", "pafy", "best_audio",
                 "title", "length", "videoid", "thumbnail")

    def __init__(self, url: str):
        self.unique_id = make_random_song_id(14)
        self.pafy: BasePafy = get_pafy(url)

        # Make sure streams are available
        if not self.pafy._have_basic:
            self.pafy._fetch_basic()

        # Find best audio stream
        audio: BaseStream = self.pafy.getbestaudio(ftypestrict=False)

        if audio is None:
            raise NoAudioStream(f"no audio streams in {self.pafy.videoid}")

        self.best_audio = audio

        # Commonly used attributes
        self.title = self.pafy.title
        self.length = self.pafy.length
        self.videoid = self.pafy.videoid

        self.thumbnail = None
        # Tries better qualities first, falls back to worse ones
        if self.pafy.bigthumbhd is not None:
            self.thumbnail = self.pafy.bigthumbhd
        elif self.pafy.bigthumb is not None:
            self.thumbnail = self.pafy.bigthumb
        else:
            self.thumbnail = self.pafy.thumb

        # TODO fetch gdata in the background

    def __repr__(self):
        return f"<YoutubeAudio '{self.videoid}',{resolve_time(self.length)}>"

    def __eq__(self, other):
        if type(other) is YoutubeAudio:
            return self.unique_id == other.unique_id
        else:
            return False
