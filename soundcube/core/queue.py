# coding=utf-8
import logging
from typing import List

from .youtube import YoutubeAudio
from .exceptions import QueueException

log = logging.getLogger(__name__)


class PlayerQueue:
    def __init__(self):
        self.queue: List[YoutubeAudio] = []
        # Index of the music in queue that is currently playing
        self._current: int = None

    def append_to_queue(self, audio: YoutubeAudio):
        """
        Add a song to the end of the queue
        :param audio: YoutubeAudio object to queue
        """
        self.queue.append(audio)

        log.info(f"Added new song to queue: {audio.title}")
        log.debug(f"New state of the queue: {self.queue}")

    def insert_into_queue(self, audio: YoutubeAudio, position: int):
        """
        Insert the song at a certain point in the queue
        :param audio: YoutubeAudio to queue
        :param position: index of where to queue it
        """
        self.queue.insert(position, audio)

        log.info(f"Inserted new track to queue at index {position}: {audio.title}")
        log.debug(f"New state of the queue: {self.queue}")

    def remove_from_queue(self, position: int):
        """
        Remove a queued song at the provided index (position).
        :param position: index of a song in the queue
        """
        try:
            title = self.queue[position].title
            del self.queue[position]
        except IndexError:
            raise QueueException("invalid position")

        log.info(f"Removed a track from the queue at position: {position} ({title})")
        log.debug(f"New state of the queue: {self.queue}")

    @property
    def current_audio(self):
        """
        :return: the current song
        """
        if not self.queue:
            return None

        try:
            return self.queue[self._current]
        except (IndexError, TypeError):
            raise QueueException("no current song")

    @property
    def next_audio(self):
        """
        Updates the current index with the next song.
        :return: the new song
        """
        # Check if there is a next song
        if (self._current + 1) > (len(self.queue) - 1):
            # There is no next song
            return None

        self._current += 1
        return self.current_audio

    @property
    def previous_audio(self):
        """
        Updates the current index with the previous song.
        :return: the new song
        """
        # Check if there is a next song
        if (self._current - 1) < 0:
            # There is no previous song
            return None

        self._current -= 1
        return self.current_audio

    def set_current_song(self, index: int):
        """
        Manually sets the current song by index.
        """
        if index > (len(self.queue) - 1):
            raise QueueException("this index doesn't exist")

        self._current = index

    def get_song_at(self, index: int):
        """
        Function for getting a song at a specified index
        :param index: song's index in the queue
        :return: YoutubeAudio object

        :raise: QueueException: there is no song at that index
        """
        try:
            return self.queue[index]
        except IndexError:
            raise QueueException("this index doesn't exist")
