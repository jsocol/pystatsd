from functools import wraps
import random
import socket
import threading
import time


class _Timer(object):
    """A contextdecorator for timing."""
    _local = threading.local()

    def __init__(self, cl):
        self.client = cl

    def __delattr__(self, attr):
        """Store thread-local data safely."""
        delattr(self._local, attr)

    def __getattr__(self, attr):
        """Store thread-local data safely."""
        return getattr(self._local, attr)

    def __setattr__(self, attr, value):
        """Store thread-local data safely."""
        setattr(self._local, attr, value)

    def __call__(self, stat, rate=1):
        if callable(stat):  # As a decorator, stat may be a function.
            @wraps(stat)
            def wrapped(*a, **kw):
                with self:
                    return stat(*a, **kw)
            return wrapped
        self.stat = stat
        self.rate = rate
        return self

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, typ, value, tb):
        dt = time.time() - self.start
        dt = int(round(dt * 1000))  # Convert to ms.
        self.client.timing(self.stat, dt, self.rate)
        del self.start, self.stat, self.rate  # Clean up.
        return False


class StatsClient(object):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None):
        """Create a new client."""
        self._addr = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.prefix = prefix
        self.timer = _Timer(self)

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
