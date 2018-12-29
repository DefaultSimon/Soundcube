# coding=utf-8
import vlc
import logging
import asyncio
import time

from .youtube import get_audio_url, get_pafy
from .exceptions import PlayerException
from .utilities import resolve_time, clamp
from ..config import DEFAULT_VOLUME, VOLUME_STEP

log = logging.getLogger(__name__)


class Player:
    def __init__(self, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.vlc: vlc.Instance = vlc.Instance()
        self.player: vlc.MediaPlayer = self.vlc.media_player_new()

        self.loop = loop

        self._current_volume = self._last_volume = DEFAULT_VOLUME
        self._is_muted = False

    # TODO transform to proper typing
    async def play(self, url: str) -> object:
        t_init = time.time()

        obj = get_pafy(url)
        audio = get_audio_url(pafy_=obj)

        log.debug(f"Got audio url from {obj.title}: {audio}")

        media_obj: vlc.Media = self.vlc.media_new(audio)
        if media_obj is None:
            raise PlayerException("Error while trying to create new Media object for VLC")

        log.info("Updating media on player...")
        self.player.set_media(media_obj)

        self.player.play()

        # Show info
        delta = round(time.time() - t_init, 2)
        log.info(f"Playing: {obj.title} (length: {resolve_time(obj.length)}), timedelta: {delta}s")

        return obj

    async def pause(self) -> bool:
        if not self.player.is_playing():
            return False

        self.player.pause()
        return True

    async def resume(self) -> bool:
        if self.player.is_playing():
            return False

        self.player.play()
        return True

    ###################
    # VOLUME FUNCTIONS
    ###################
    def get_volume(self) -> int:
        return int(self.player.audio_get_volume())

    def set_volume(self, amount: int) -> None:
        amount = clamp(amount, 0, 100)

        # Store previous volume so we can mute and unmute
        self._last_volume = self._current_volume
        self._current_volume = amount

        self.player.audio_set_volume(amount)

    async def volume_up(self, amount=VOLUME_STEP) -> int:
        new_volume = clamp(self.get_volume() + amount, 0, 100)

        self.set_volume(new_volume)
        return new_volume

    async def volume_down(self, amount=VOLUME_STEP) -> int:
        new_volume = clamp(self.get_volume() - amount, 0, 100)

        self.set_volume(new_volume)
        return new_volume

    async def mute(self) -> bool:
        if self._is_muted:
            return False

        self.set_volume(0)
        self._is_muted = True
        return True

    async def unmute(self) -> bool:
        if self._is_muted:
            return False

        self.set_volume(self._last_volume)
        self._is_muted = False
        return True
