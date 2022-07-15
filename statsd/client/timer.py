from __future__ import annotations

import functools
from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from time import perf_counter
from types import TracebackType
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .base import StatsClientBase

    R = TypeVar("R")
    C = TypeVar("C", bound=StatsClientBase)


def safe_wraps(
    wrapper: Callable[..., R] | functools.partial[R],
    *args: Sequence[str],
    **kwargs: Sequence[str],
) -> Callable[..., Callable[..., R]]:
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func
    return functools.wraps(wrapper, *args, **kwargs)


class Timer:
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client: C, stat: str, rate: float = 1):
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms: float | None = None
        self._sent = False
        self._start_time: float | None = None

    def __call__(self, f: Callable[..., R]) -> Callable[..., R]:
        """Thread-safe timing function decorator."""

        @safe_wraps(f)
        def _wrapped(*args: object, **kwargs: object) -> R:
            start_time = perf_counter()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (perf_counter() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)  # type: ignore[no-untyped-call]

        return _wrapped

    def __enter__(self) -> Timer:
        return self.start()

    def __exit__(
        self,
        typ: type[BaseException] | None,
        value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop()

    def start(self) -> Timer:
        self.ms = None
        self._sent = False
        self._start_time = perf_counter()
        return self

    def stop(self, send: bool = True) -> Timer:
        if self._start_time is None:
            raise RuntimeError("Timer has not started.")
        dt = perf_counter() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self) -> None:
        if self.ms is None:
            raise RuntimeError("No data recorded.")
        if self._sent:
            raise RuntimeError("Already sent data.")
        self._sent = True
        self.client.timing(self.stat, self.ms, self.rate)  # type: ignore[no-untyped-call]
