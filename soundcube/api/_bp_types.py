# coding=utf-8


class StatusType:
    OK = "ok"
    ERROR = "error"
    FORBIDDEN = "forbidden"
    # No operation
    NOOP = "noop"
    # Error, but non-planned
    INTERNAL_ERROR = "internal_error"
    BAD_REQUEST = "bad_request"


class PlayType:
    NEXT = "next"
    QUEUE = "queue"
    AT_POSITION = "at_position"
