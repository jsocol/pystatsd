from contextlib import contextmanager
from functools import wraps
import random
import socket
import time


class Timer(object):
    """A contextdecorator for timing."""
    stat = None
    rate = None

    def __init__(self, cl):
        self.client = cl

    def __call__(self, stat, rate=1):
        self.stat = stat
        self.rate = rate
        this = self
        def decorator(fn):
            @wraps(fn)
            def wrapped(*a, **kw):
                with this:
                    return fn(*a, **kw)
            return wrapped
        return decorator

    def __enter__(self, stat=None, rate=None):
        self.start = time.time()
        if stat is not None:
            self.stat = stat
        elif self.stat is None:
            raise TypeError("'stat' is not defined")

        if rate is not None:
            self.rate = rate
        elif self.rate is None:
            raise TypeError("'rate' is not defined")

    def __exit__(self, typ, value, tb):
        dt = time.time() - self.start
        dt = int(round(dt * 1000))  # Convert to ms.
        self.client.timing(self.stat, dt, self.rate)
        if any((typ, value, rb)):
            raise typ, value, tb


class StatsClient(object):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None):
        """Create a new client."""
        self._addr = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.prefix = prefix
        self.timer = Timer(self)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        self._send(stat, '%d|ms' % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        self._send(stat, '%d|c' % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def _send(self, stat, value, rate=1):
        """Send data to statsd."""
        if rate < 1:
            if random.random() < rate:
                value = '%s|@%s' % (value, rate)
            else:
                return

        if self.prefix:
            stat = '%s.%s' % (self.prefix, stat)

        try:
            self._sock.sendto('%s:%s' % (stat, value), self._addr)
        except socket.error:
            # No time for love, Dr. Jones!
            pass
