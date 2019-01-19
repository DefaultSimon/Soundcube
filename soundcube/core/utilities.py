# coding=utf-8
#################
# Utilities
#################
import uuid
from typing import Union


class Singleton(type):
    """
    Only allows one instantiation. On subsequent __init__ calls, returns the first instance
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def clamp(value: Union[int, float], min_: Union[int, float], max_: Union[int, float]) -> Union[int, float]:
    """
    Clamps the value between minimum and maximum values.
    :param value: number to clamp
    :param min_: minimum value
    :param max_: maximum value
    :return: clamped number
    """
    # If inside the boundaries, return the actual value
    if min_ <= value <= max_:
        return value
    # When going over the boundary, return min/max
    elif value < min_:
        return min_
    else:
        return max_


def resolve_time(delta: int, sep: str = "") -> str:
    """
    Converts an int to its human-friendly representation
    :param delta: time in seconds
    :param sep: string separator
    :return: string
    """
    if type(delta) is not int:
        delta = int(delta)

    years, days, hours, minutes = 0, 0, 0, 0

    # Calculate best representations of the number
    while True:
        if delta >= 60 * 60 * 24 * 365:  # 1 Year
            years += 1
            delta -= 31556926

        if delta >= 60 * 60 * 24:  # 1 Day
            days += 1
            delta -= 86400

        elif delta >= 60 * 60:  # 1 hour
            hours += 1
            delta -= 3600

        elif delta >= 60:  # 1 minute
            minutes += 1
            delta -= 60

        else:
            break

    # Form calculations into a string
    fields = []
    if years:
        fields.append(f"{years}y")
    if days:
        fields.append(f"{days}d")
    if hours:
        fields.append(f"{hours}h")
    if minutes:
        fields.append(f"{minutes}m")
    fields.append(f"{delta}s")

    # If tm is less than a minute, do not add "and".
    return sep.join(fields)


def make_random_song_id(length=12) -> int:
    return int(str(uuid.uuid4().int)[:length])
