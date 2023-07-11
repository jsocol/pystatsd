import functools
from inspect import iscoroutinefunction
from time import perf_counter as time_now
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Optional, Type, TypeVar


if TYPE_CHECKING:
    from statsd.client.base import StatsClientBase


_F = TypeVar('_F', bound=Callable[..., Any])
_TimerT = TypeVar('_TimerT', bound='Timer')


def _safe_wraps(wrapper, *args, **kwargs):
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func
    return functools.wraps(wrapper, *args, **kwargs)


class Timer:
    """A context manager/decorator for statsd.timing()."""

    client: 'StatsClientBase'
    stat: str
    rate: float
    ms: Optional[float]

    def __init__(self, client: 'StatsClientBase', stat: str,
                 rate: float = 1) -> None:
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None
        self._sent = False
        self._start_time = None

    def __call__(self, f: _F) -> _F:
        """Thread-safe timing function decorator."""
        if iscoroutinefunction(f):
            @_safe_wraps(f)
            async def _async_wrapped(*args, **kwargs):
                start_time = time_now()
                try:
                    return await f(*args, **kwargs)
                finally:
                    elapsed_time_ms = 1000.0 * (time_now() - start_time)
                    self.client.timing(self.stat, elapsed_time_ms, self.rate)
            return _async_wrapped

        @_safe_wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time_now()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (time_now() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)
        return _wrapped

    def __enter__(self: _TimerT) -> _TimerT:
        return self.start()

    def __exit__(
        self,
        typ: Optional[Type[BaseException]],
        value: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.stop()

    def start(self: _TimerT) -> _TimerT:
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self: _TimerT, send: bool = True) -> _TimerT:
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
