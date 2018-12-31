# coding=utf-8


class SoundcubeException(Exception):
    """
    Base class for all exceptions
    """
    pass


# PLAYER EXCEPTIONS
class PlayerException(SoundcubeException):
    """
    Raised for general player-related problems
    """
    pass


class MediaNotLoaded(PlayerException):
    """
    Raised when the user tries playing an unloaded song
    """
    pass


# MEDIA EXCEPTIONS
class MediaException(SoundcubeException):
    """
    Raised for general media/audio-related problems
    """
    pass


class NoAudioStream(MediaException):
    """
    Raised when the requested media has no audio streams
    """
    pass


# QUEUE EXCEPTIONS
class QueueException(SoundcubeException):
    """
    Raised for general queue-related problems
    """
    pass


# USER EXCEPTIONS
class YoutubeException(SoundcubeException):
    """
    Raised for YouTube-related problems (such as an invalid link)
    """
    pass
