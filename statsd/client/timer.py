from __future__ import absolute_import, division, unicode_literals

import functools
from typing import TYPE_CHECKING, Callable, Optional, TypeVar

# Use timer that's not susceptible to time of day adjustments.
try:
    # perf_counter is only present on Py3.3+
    from time import perf_counter as time_now
except ImportError:
    # fall back to using time
    from time import time as time_now


if TYPE_CHECKING:
    from .base import StatsClientBase


F = TypeVar('F', bound=Callable)
C = TypeVar('C', bound=Callable)
T = TypeVar('T', bound='Timer')


def safe_wraps(wrapper: F, *args, **kwargs) -> Callable[[C], C]:
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func  # type: ignore[assignment]
    return functools.wraps(wrapper, *args, **kwargs)


class Timer(object):
    """A context manager/decorator for statsd.timing()."""
    client: 'StatsClientBase'
    stat: str
    rate: float
    ms: Optional[float]
    _sent: bool
    _start_time: Optional[float]

    def __init__(self, client: 'StatsClientBase',
                 stat: str, rate: float = 1) -> None:
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None
        self._sent = False
        self._start_time = None

    def __call__(self, f: F) -> F:
        """Thread-safe timing function decorator."""
        @safe_wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time_now()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (time_now() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)
        return _wrapped  # type: ignore[return-value]

    def __enter__(self: T) -> T:
        return self.start()

    def __exit__(self, *exc_info) -> None:
        self.stop()

    def start(self: T) -> T:
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self: T, send: bool = True) -> T:
        if self._start_time is None:
            raise RuntimeError('Timer has not started.')
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self) -> None:
        if self.ms is None:
            raise RuntimeError('No data recorded.')
        if self._sent:
            raise RuntimeError('Already sent data.')
        self._sent = True
        self.client.timing(self.stat, self.ms, self.rate)
