from __future__ import with_statement
from functools import wraps
import random
import socket
import time


__all__ = ['StatsClient']


class Timer(object):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1):
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kw):
            with self:
                return f(*args, **kw)
        return wrapper

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, typ, value, tb):
        dt = time.time() - self.start
        self.ms = int(round(1000 * dt))  # Convert to ms.
        self.client.timing(self.stat, self.ms, self.rate)


class StatsClient(object):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None):
        """Create a new client."""
        self._addr = (socket.gethostbyname(host), port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._prefix = prefix

    def _after(self, data):
        self._send(data)

    def pipeline(self):
        return Pipeline(self)

    def timer(self, stat, rate=1):
        return Timer(self, stat, rate)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        data = self._prepare(stat, '%d|ms' % delta, rate)
        if data is not None:
            self._after(data)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        data = self._prepare(stat, '%s|c' % count, rate)
        if data is not None:
            self._after(data)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1, delta=False):
        """Set a gauge value."""
        prefix = '+' if delta and value >= 0 else ''
        value = '%s%s|g' % (prefix, value)
        data = self._prepare(stat, value, rate)
        if data is not None:
            self._after(data)

    def set(self, stat, value, rate=1):
        """Set a set value."""
        data = self._prepare(stat, '%s|s' % value, rate)
        if data is not None:
            self._after(data)

    def _prepare(self, stat, value, rate=1):
        if rate < 1:
            if random.random() < rate:
                value = '%s|@%s' % (value, rate)
            else:
                return

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        data = '%s:%s' % (stat, value)
        return data

    def _send(self, data):
        """Send data to statsd."""
        try:
            self._sock.sendto(data.encode('ascii'), self._addr)
        except socket.error:
            # No time for love, Dr. Jones!
            pass


class Pipeline(StatsClient):
    def __init__(self, client):
        self._client = client
        self._prefix = client._prefix
        self._stats = []

    def _after(self, data):
        self._stats.append(data)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        self.send()

    def send(self):
        # Use pop(0) to preserve the order of the stats.
        if not self._stats:
            return
        data = self._stats.pop(0)
        while self._stats:
            stat = self._stats.pop(0)
            if len(stat) + len(data) + 1 >= 512:
                self._client._after(data)
                data = stat
            else:
                data += '\n' + stat
        if data:
            self._client._after(data)
