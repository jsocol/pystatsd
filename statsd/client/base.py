from __future__ import absolute_import, division, unicode_literals

import random
from collections import deque
from datetime import timedelta
from typing import Deque, Optional, TypeVar, Union

from .timer import Timer


P = TypeVar('P', bound='PipelineBase')


class StatsClientBase(object):
    """A Base class for various statsd clients."""
    _prefix: Optional[str]

    def close(self) -> None:
        """Used to close and clean up any underlying resources."""
        raise NotImplementedError()

    def _send(self) -> None:
        raise NotImplementedError()

    def pipeline(self) -> 'PipelineBase':
        raise NotImplementedError()

    def timer(self, stat: str, rate: float = 1) -> Timer:
        return Timer(self, stat, rate)

    def timing(
        self,
        stat: str,
        delta: Union[timedelta, float],
        rate: float = 1,
    ) -> None:
        """
        Send new timing information.

        `delta` can be either a number of milliseconds or a timedelta.
        """
        if isinstance(delta, timedelta):
            # Convert timedelta to number of milliseconds.
            delta = delta.total_seconds() * 1000.
        self._send_stat(stat, '%0.6f|ms' % delta, rate)

    def incr(self, stat: str, count: int = 1, rate: float = 1) -> None:
        """Increment a stat by `count`."""
        self._send_stat(stat, '%s|c' % count, rate)

    def decr(self, stat: str, count: int = 1, rate: float = 1) -> None:
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(
        self,
        stat: str,
        value: float,
        rate: float = 1,
        delta: bool = False,
    ) -> None:
        """Set a gauge value."""
        if value < 0 and not delta:
            if rate < 1:
                if random.random() > rate:
                    return
            with self.pipeline() as pipe:
                pipe._send_stat(stat, '0|g', 1)
                pipe._send_stat(stat, '%s|g' % value, 1)
        else:
            prefix = '+' if delta and value >= 0 else ''
            self._send_stat(stat, '%s%s|g' % (prefix, value), rate)

    def set(self, stat: str, value: str, rate: float = 1) -> None:
        """Set a set value."""
        self._send_stat(stat, '%s|s' % value, rate)

    def _send_stat(self, stat: str, value: str, rate: float) -> None:
        self._after(self._prepare(stat, value, rate))

    def _prepare(self, stat: str, value: str, rate: float) -> Optional[str]:
        if rate < 1:
            if random.random() > rate:
                return None
            value = '%s|@%s' % (value, rate)

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        return '%s:%s' % (stat, value)

    def _after(self, data: Optional[str]) -> None:
        if data:
            self._send(data)


class PipelineBase(StatsClientBase):
    _prefix: Optional[str]
    _stats: Deque[str]
    _client: StatsClientBase

    def __init__(self, client: StatsClientBase) -> None:
        self._client = client
        self._prefix = client._prefix
        self._stats = deque()

    def _send(self) -> None:
        raise NotImplementedError()

    def _after(self, data: Optional[str]) -> None:
        if data is not None:
            self._stats.append(data)

    def __enter__(self: P) -> P:
        return self

    def __exit__(self, *exc_info) -> None:
        self.send()

    def send(self) -> None:
        if not self._stats:
            return
        self._send()

    def pipeline(self: P) -> P:
        return self.__class__(self)
