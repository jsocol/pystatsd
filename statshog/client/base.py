from __future__ import absolute_import, division, unicode_literals

import random
from collections import deque
from datetime import timedelta
from typing import Deque, Dict, Union

Tags = Union[Dict[str, Union[str, int]], None]


class StatsClientBase(object):
    """A Base class for various statsd clients."""

    _prefix: Union[str, None]
    _telegraf: bool

    def close(self):
        """Used to close and clean up any underlying resources."""
        raise NotImplementedError()

    def pipeline(self):
        raise NotImplementedError()

    def timer(self, stat: str, rate: float = 1.0, tags: Tags = None):
        from .timer import Timer

        return Timer(self, stat, rate, tags)

    def timing(
        self,
        stat: str,
        delta: Union[timedelta, int, float],
        rate: float = 1.0,
        tags: Tags = None,
    ):
        """
        Send new timing information.

        `delta` can be either a number of milliseconds or a timedelta.
        """
        if isinstance(delta, timedelta):
            # Convert timedelta to number of milliseconds.
            delta = delta.total_seconds() * 1000.0
        self._send_stat(stat, "%0.6f|ms" % delta, rate, tags)

    def incr(self, stat: str, count: int = 1, rate: float = 1.0, tags: Tags = None):
        """Increment a stat by `count`."""
        self._send_stat(stat, "%s|c" % count, rate, tags)

    def decr(self, stat: str, count: int = 1, rate: float = 1.0, tags: Tags = None):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate, tags)

    def gauge(
        self,
        stat: str,
        value: int,
        rate: float = 1.0,
        delta: bool = False,
        tags: Tags = None,
    ):
        """Set a gauge value."""
        if value < 0 and not delta:
            if rate < 1:
                if random.random() > rate:
                    return
            with self.pipeline() as pipe:
                pipe._send_stat(stat, "0|g", 1, tags)
                pipe._send_stat(stat, "%s|g" % value, 1, tags)
        else:
            prefix = "+" if delta and value >= 0 else ""
            self._send_stat(stat, "%s%s|g" % (prefix, value), rate, tags)

    def set(self, stat: str, value: int, rate: float = 1.0, tags: Tags = None):
        """Set a set value."""
        self._send_stat(stat, "%s|s" % value, rate, tags)

    def _send_stat(self, stat, value, rate, tags: Tags = None):
        self._after(self._prepare(stat, value, rate, tags))

    def _prepare(self, stat: str, value, rate, tags: Tags = None):
        if rate < 1:
            if random.random() > rate:
                return
            value = "%s|@%s" % (value, rate)

        if self._prefix:
            stat = "%s.%s" % (self._prefix, stat)

        if tags:
            if self._telegraf:
                return f"{stat},{make_tags(tags)}:{value}"
            else:
                raise ValueError("Tags are not supported without telegraf support")

        return "%s:%s" % (stat, value)

    def _after(self, data):
        if data:
            self._send(data)


class PipelineBase(StatsClientBase):
    _stats: Deque[str]

    def __init__(self, client: StatsClientBase):
        self._client = client
        self._prefix = client._prefix
        self._stats = deque()

    def _send(self):
        raise NotImplementedError()

    def _after(self, data: str):
        if data is not None:
            self._stats.append(data)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        self.send()

    def send(self):
        if not self._stats:
            return
        self._send()

    def pipeline(self):
        return self.__class__(self)


def make_tags(tags: Dict[str, Union[str, int]]):
    return ",".join(f"{k}={v}" for k, v in tags.items())
