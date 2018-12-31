# coding=utf-8
import vlc
import logging
import asyncio
import time

from .youtube import YoutubeAudio
from .exceptions import PlayerException, SoundcubeException, QueueException, YoutubeException
from .utilities import resolve_time, clamp
from .queue import PlayerQueue

from ..config import DEFAULT_VOLUME, VOLUME_STEP
from ..api._bp_types import PlayType

log = logging.getLogger(__name__)


class Player:
    def __init__(self, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.vlc: vlc.Instance = vlc.Instance()
        self.player: vlc.MediaPlayer = self.vlc.media_player_new()

        self._queue = PlayerQueue()

        self.loop: asyncio.AbstractEventLoop = loop

        self._current_volume = self._last_volume = DEFAULT_VOLUME
        self._is_muted: bool = False

    ###################
    # PLAYING FUNCTIONS
    ###################
    async def queue(self, url: str, play_type: PlayType = PlayType.QUEUE):
        """
        Put a new song in the player queue.
        :param url: Youtube url to queue
        :param play_type: when to play this audio

        :raise: SoundcubeException: play_type is invalid
        """
        t_init = time.time()

        try:
            audio = YoutubeAudio(url)
        except OSError:
            raise YoutubeException("invalid link")

        log.debug(f"Got audio from '{audio.title}':{audio.best_audio}, parsing took {round(time.time() - t_init, 3)}")

        # Puts the song at the end of queue
        if play_type == PlayType.QUEUE:
            self._queue.add_to_queue(audio)
        # Always puts the song after the current one
        elif play_type == PlayType.NEXT:
            next_index = self._queue._current + 1
            self._queue.insert_into_queue(audio, next_index)
        else:
            raise SoundcubeException(f"invalid PlayType: '{play_type}'")

    async def play(self) -> YoutubeAudio:
        """
        Plays the current song in queue.
        :return: YoutubeAudio object

        :raise: QueueException: no song in queue
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        # If no song is set, start with the first one
        if self._queue._current is None:
            self._queue.set_current_song(0)

        # Get current song from queue
        audio: YoutubeAudio = self._queue.current_audio

        if audio is None:
            raise QueueException("no song to play")

        self._update_media(audio)
        self.player.play()

        # Show info and return
        self._show_play_info()

        return audio

    async def pause(self) -> bool:
        """
        Pauses the current song (if one is playing).

        :return: bool indicating if the song was paused
        """
        if not self.player.is_playing():
            log.info("Tried to pause, was not even playing")
            return False

        self.player.pause()
        log.info("Song paused")
        return True

    async def resume(self) -> bool:
        """
        Resume the current song (and load one if not already via play()).

        :return: bool indicating if the song was resumed

        :raise: QueueException: no song in queue
        """
        if self.player.is_playing():
            log.info("Tried to resume, was already playing")
            return False

        # If no tracks are loaded, try loading the current song first
        if not self.player.get_media():
            await self.play()
        else:
            self.player.play()
            log.info("Song resumed")

        return True

    async def stop(self) -> bool:
        """
        Stops the current song (if one is playing).

        :return: bool indicating if the song was stopped
        """
        # First pause, then unload
        if not self.player.get_media():
            return False

        was_playing = await self.pause()

        self.player.set_media(None)
        return was_playing

    async def next(self) -> YoutubeAudio:
        """
        Play next song in queue
        :return: YoutubeAudio object

        :raise: QueueException: no next song
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        audio: YoutubeAudio = self._queue.next_audio
        if not audio:
            raise QueueException("no next song")

        self._update_media(audio)
        self.player.play()

        # Show info and return
        self._show_play_info()

        return audio

    async def previous(self) -> YoutubeAudio:
        """
        Play previous song in queue
        :return: YoutubeAudio object

        :raise: QueueException: no next song
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        audio: YoutubeAudio = self._queue.previous_audio
        if not audio:
            raise QueueException("no previous song")

        self._update_media(audio)
        self.player.play()

        # Show info and return
        self._show_play_info()

        return audio

    async def set_time(self, time_: float):
        """

        :param time_:
        :return:
        """
        if type(time_) not in [int, float]:
            raise RuntimeError(f"'time': expected float, got {type(time)}")

        self.player.set_time(int(time_ * 1000))

    ###################
    # VOLUME FUNCTIONS
    ###################
    def get_volume(self) -> int:
        """
        Returns the player volume.
        :return: int - volume (0-100)
        """
        return int(self.player.audio_get_volume())

    def set_volume(self, amount: int):
        """
        Sets the player volume.
        :param amount: int between 0 and 100
        """
        amount = clamp(amount, 0, 100)

        # Store previous volume so we can mute and unmute
        self._last_volume = self._current_volume
        self._current_volume = amount

        self.player.audio_set_volume(amount)

    def volume_increase(self, amount: int = VOLUME_STEP) -> int:
        """
        Shorthand function for setting a louder volume.
        :param amount: int between 0 and 100
        :return: int - new volume
        """
        new_volume = clamp(self.get_volume() + amount, 0, 100)

        self.set_volume(new_volume)
        return new_volume

    def volume_decrease(self, amount: int = VOLUME_STEP) -> int:
        """
        Shorthand function for setting a quieter volume.
        :param amount: int between 0 and 100
        :return: int - new volume
        """
        new_volume = clamp(self.get_volume() - amount, 0, 100)

        self.set_volume(new_volume)
        return new_volume

    def mute(self) -> bool:
        """
        Mute the sound output (set volume to 0) and remember the previous volume.
        :return: bool indicating if the mute was done
        """
        if self._is_muted:
            return False

        self.set_volume(0)
        self._is_muted = True
        return True

    def unmute(self) -> bool:
        """
        Unmute the sound output (set volume to previous one).
        :return: bool indicating if the unmute was done
        """
        if self._is_muted:
            return False

        self.set_volume(self._last_volume)
        self._is_muted = False
        return True

    ###################
    # INTERNAL FUNCTIONS
    ###################
    def _update_media(self, audio: YoutubeAudio):
        media_obj: vlc.Media = self.vlc.media_new(audio.best_audio.url)
        if media_obj is None:
            raise PlayerException("Error while creating vlc Media object")

        self.player.set_media(media_obj)
        log.info("Updated Media on player")

    def _show_play_info(self):
        audio = self._queue.current_audio
        log.info(f"Playing: {audio.title} (length: {resolve_time(audio.length)})")
