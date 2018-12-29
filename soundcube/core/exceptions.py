# coding=utf-8


class SoundcubeException(Exception):
    """
    Base class for all exceptions
    """
    pass


class PlayerException(SoundcubeException):
    """
    Raised for general player-related problems
    """
    pass
