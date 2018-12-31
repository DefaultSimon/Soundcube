# coding=utf-8


class StatusType:
    OK = "ok"
    ERROR = "error"
    FORBIDDEN = "forbidden"
    # No operation
    NOOP = "noop"
    # Error, but non-planned
    INTERNAL_ERROR = "internal_error"


class PlayType:
    NEXT = "next"
    QUEUE = "queue"
