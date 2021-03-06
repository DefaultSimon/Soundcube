# coding=utf-8
import vlc
import logging
import asyncio
import time

from typing import Union

from .youtube import YoutubeAudio
from .exceptions import PlayerException, SoundcubeException, QueueException, YoutubeException, OutsideTimeBounds
from .utilities import resolve_time, clamp, Singleton
from .queue import PlayerQueue

from ..config import DEFAULT_VOLUME
from ..api._bp_types import PlayType

log = logging.getLogger(__name__)


class Player(metaclass=Singleton):
    def __init__(self, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.vlc: vlc.Instance = vlc.Instance()
        self.player: vlc.MediaPlayer = self.vlc.media_player_new()

        self._queue: PlayerQueue = PlayerQueue()

        self.loop: asyncio.AbstractEventLoop = loop

        self._current_volume = DEFAULT_VOLUME
        self.set_volume(self._current_volume)

    ###################
    # PLAYER FUNCTIONS
    # Note: player_queue is both a Player and Queue function
    ###################
    async def player_queue(self, url: str, play_type: PlayType = PlayType.QUEUE, position: int = None, set_playing: bool = False):
        """
        Put a new song in the player queue.
        :param url: Youtube url to queue
        :param play_type: when to play this audio
        :param position: when using PlayType.AT_POSITION, this is the position to place the song
        :param set_playing: bool indicating if the new song should be loaded (but not yet played)

        :raise: SoundcubeException: play_type is invalid
        """
        t_init = time.time()

        try:
            audio = YoutubeAudio(url)
        except OSError:
            raise YoutubeException("invalid link")

        queue_was_empty = self._queue.current_audio is None

        log.debug(f"Got audio from '{audio.title}':{audio.best_audio}, parsing took {round(time.time() - t_init, 3)}")

        # All if clauses keep track of song_index for use later
        # Puts the song at the end of queue
        if play_type == PlayType.QUEUE:
            song_index = self._queue.append_to_queue(audio)
        # Always puts the song after the current one
        elif play_type == PlayType.NEXT:
            song_index = self._queue.current_index + 1
            self._queue.insert_into_queue(audio, song_index)
        elif play_type == PlayType.AT_POSITION:
            if position is None:
                raise RuntimeError("missing arguments")

            song_index = position
            self._queue.insert_into_queue(audio, position)
        else:
            raise SoundcubeException(f"invalid PlayType: '{play_type}'")

        # Load the song if specified or if it is the first song
        if set_playing is True or queue_was_empty:
            self._queue.set_current_song(song_index)
            await self.player_load()

    async def player_load(self) -> YoutubeAudio:
        """
        Loads the current song
        :return: YoutubeAudio that was loaded
        """
        # If no song is set, start with the first one
        if self._queue.current_index is None:
            raise QueueException("no song is loaded")

        # Get current song:
        audio: YoutubeAudio = self._queue.current_audio

        self._update_media(audio)
        return audio

    async def player_play(self) -> YoutubeAudio:
        """
        Plays the current song in queue.
        :return: YoutubeAudio object

        :raise: QueueException: no song in queue
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        # If no song is set, start with the first one
        if self._queue.current_index is None:
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

    async def player_pause(self) -> bool:
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

    async def player_resume(self) -> bool:
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
            await self.player_play()
        else:
            self.player.play()
            log.info("Song resumed")

        return True

    async def player_stop(self) -> bool:
        """
        Stops the current song (if one is playing).

        :return: bool indicating if the song was stopped
        """
        # First pause, then unload
        if not self.player.get_media():
            return False

        was_playing = await self.player_pause()

        self.player.set_media(None)
        return was_playing

    async def player_next(self) -> YoutubeAudio:
        """
        Play next song in queue
        :return: YoutubeAudio object

        :raise: QueueException: no next song
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        audio: YoutubeAudio = self._queue.next_audio
        if not audio:
            raise QueueException("no next song")

        if self.player_is_playing():
            await self.player_stop()

        self._update_media(audio)
        self.player.play()

        # Show info and return
        self._show_play_info()

        return audio

    async def player_previous(self) -> YoutubeAudio:
        """
        Play previous song in queue
        :return: YoutubeAudio object

        :raise: QueueException: no next song
        :raise: PlayerException: problem while trying to create a new Media instance
        """
        audio: YoutubeAudio = self._queue.previous_audio
        if not audio:
            raise QueueException("no previous song")

        if self.player_is_playing():
            await self.player_stop()

        self._update_media(audio)
        self.player.play()

        # Show info and return
        self._show_play_info()

        return audio

    async def player_set_time(self, time_: float):
        """
        Sets the time for the current song.

        :param time_: time to set in seconds
        :return: bool indicating if the time was changed

        :raise: OutsideTimeBounds: requested time is outside the audio bounds
        """
        if type(time_) not in [int, float]:
            raise RuntimeError(f"'time': expected float, got {type(time)}")

        if not self.player.get_media():
            return False

        # Find the current song length
        audio_length = self._queue.current_audio.length

        if time_ > audio_length:
            raise OutsideTimeBounds("invalid time")

        self.player.set_time(int(time_ * 1000))
        return True

    def player_is_playing(self) -> bool:
        """
        :return: a boolean indicating if a song is currently being played
        """
        if not self.player.get_media():
            return False

        return bool(self.player.is_playing())

    def player_is_song_loaded(self) -> bool:
        """
        :return: A boolean indicating if a song is loaded / loading.
        """
        return bool(self.player.get_media())

    async def player_get_time(self) -> Union[None, float]:
        """
        :return: None if no song is being played
        :return: float representing seconds of time
        """
        time_ms = self.player.get_time()

        # Returned by vlc module if there is no media
        if time_ms == -1:
            return None
        else:
            return time_ms / 1000

    ###################
    # QUEUE FUNCTIONS
    ###################
    async def queue_remove(self, position: int):
        """
        Remove a song from the queue
        :param position: song's index in the queue

        :raise: QueueException: no song at this position
        """
        # Move to a different song if playing the one that is being removed
        if self._queue.current_index == position:
            log.info("Trying to remove song, but it is playing; loading next/previous")
            try:
                # The entire queue moved up, adjust for this
                self._queue.set_current_song(self._queue.current_index - 1)

                await self.player_next()
            except QueueException:
                try:
                    await self.player_previous()
                except QueueException:
                    log.info("No song remaining, stopping")
            finally:
                await self.player_stop()

        self._queue.remove_from_queue(position)

    async def queue_move(self, current_position: int, new_index: int):
        """
        Move a song in the queue
        :param current_position: song's current index in the queue
        :param new_index: which index to move the song to

        :raise: QueueException: no song at this position
        """
        # This will raise a QueueException if the index doesn't exist,
        # so there is no need for backtracking if something goes haywire later
        audio = self._queue.get_song_at(current_position)
        audio2 = self._queue.get_song_at(new_index)

        # makes sure that (if a moved song is currently playing) the index of playing is updated as well
        if self._queue.current_audio == audio:
            update_playing_index = new_index
        elif self._queue.current_audio == audio2:
            update_playing_index = current_position
        else:
            update_playing_index = False

        # The order is reversed depending on the position of indexes
        if current_position < new_index:
            self._queue.insert_into_queue(audio, new_index + 1)
            self._queue.remove_from_queue(current_position)
        else:
            self._queue.remove_from_queue(current_position)
            self._queue.insert_into_queue(audio, new_index)

        if update_playing_index is not False:
            log.debug(f"Updating index after moving: {update_playing_index}")
            self._queue.set_current_song(update_playing_index)

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

        self.player.audio_set_volume(amount)

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
