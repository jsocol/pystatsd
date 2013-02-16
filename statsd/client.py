from __future__ import with_statement
from functools import wraps
import random
import socket
import time
import collections
try:
    from StringIO import StringIO
except ImportError:
    # Py3k!
    from io import StringIO


class _Timer(object):
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

    def __init__(self, host='localhost', port=8125, prefix=None, batch_len=1,
                 max_packet_size=400):
        """Create a new client."""
        self._addr = (socket.gethostbyname(host), port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._prefix = prefix
        self._batch_len = batch_len
        self._max_packet_size = max_packet_size
        self._stats = collections.deque()

    def timer(self, stat, rate=1):
        return _Timer(self, stat, rate)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        self._send(stat, '%d|ms' % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        self._send(stat, '%s|c' % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1):
        """Set a gauge value."""
        self._send(stat, '%s|g' % value, rate)

    def flush(self):
        """Flush the stats batching buffer."""
        if self._stats:
            stats = self._stats
            while stats:
                out = StringIO('')
                print(len(stats), "stats")
                # Break up messages into ideal packet sizes.
                while stats and (len(out.getvalue()) < self._max_packet_size):
                    out.write(stats.popleft())
                    out.write('\n')
                    print(len(out.getvalue()), 'bytes to send')

                try:
                    self._sock.sendto(
                        out.getvalue().encode('ascii').strip(), self._addr)
                except socket.error:
                    # No time for love, Dr. Jones!
                    pass
            self._stats.clear()

    def _send(self, stat, value, rate=1):
        """Send data to statsd."""
        if rate < 1:
            if random.random() < rate:
                value = '%s|@%s' % (value, rate)
            else:
                return

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        txt = '%s:%s' % (stat, value)
        self._stats.append(txt)
        if self._batch_len <= len(self._stats):
            self.flush()
