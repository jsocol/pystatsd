from __future__ import with_statement
from collections import deque
import functools
import random
import socket
import abc

# Use timer that's not susceptable to time of day adjustments.
try:
    # perf_counter is only present on Py3.3+
    from time import perf_counter as time_now
except ImportError:
    # fall back to using time
    from time import time as time_now


__all__ = ['StatsClient', 'TCPStatsClient']


def safe_wraps(wrapper, *args, **kwargs):
    """Safely wraps partial functions."""
    while isinstance(wrapper, functools.partial):
        wrapper = wrapper.func
    return functools.wraps(wrapper, *args, **kwargs)


class Timer(object):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1, tags=None):
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None
        self.tags = tags
        self._sent = False
        self._start_time = None

    def __call__(self, f):
        """Thread-safe timing function decorator."""
        @safe_wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time_now()
            try:
                return_value = f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (time_now() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)
            return return_value
        return _wrapped

    def __enter__(self):
        return self.start()

    def __exit__(self, typ, value, tb):
        self.stop()

    def start(self):
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self, send=True):
        if self._start_time is None:
            raise RuntimeError('Timer has not started.')
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self):
        if self.ms is None:
            raise RuntimeError('No data recorded.')
        if self._sent:
            raise RuntimeError('Already sent data.')
        self._sent = True
        self.client.timing(self.stat, self.ms, self.rate, self.tags)


class StatsClientBase(object):
    """A Base class for various statsd clients."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _send(self):
        pass

    @abc.abstractmethod
    def pipeline(self):
        pass

    def timer(self, stat, rate=1, tags=None):
        return Timer(self, stat, rate, tags)

    def timing(self, stat, delta, rate=1, tags=None):
        """Send new timing information. `delta` is in milliseconds."""
        self._send_stat(stat, '%0.6f|ms' % delta, rate, tags)

    def incr(self, stat, count=1, rate=1, tags=None):
        """Increment a stat by `count`."""
        self._send_stat(stat, '%s|c' % count, rate, tags)

    def decr(self, stat, count=1, rate=1, tags=None):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate, tags)

    def gauge(self, stat, value, rate=1, delta=False, tags=None):
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
            self._send_stat(stat, '%s%s|g' % (prefix, value), rate, tags)

    def set(self, stat, value, rate=1, tags=None):
        """Set a set value."""
        self._send_stat(stat, '%s|s' % value, rate, tags)

    def _send_stat(self, stat, value, rate, tags=None):
        self._after(self._prepare(stat, value, rate, tags))

    def _prepare(self, stat, value, rate, tags=None):
        if rate < 1:
            if random.random() > rate:
                return
            value = '%s|@%s' % (value, rate)

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        if tags:
            value = '%s|#%s' % (
                value, ','.join(['%s:%s' % (k, v) for k, v in tags.items()])
            )
        return '%s:%s' % (stat, value)

    def _after(self, data):
        if data:
            self._send(data)


class StatsClient(StatsClientBase):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None,
                 maxudpsize=512, ipv6=False):
        """Create a new client."""
        fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            host, port, fam, socket.SOCK_DGRAM)[0]
        self._addr = addr
        self._sock = socket.socket(family, socket.SOCK_DGRAM)
        self._prefix = prefix
        self._maxudpsize = maxudpsize

    def _send(self, data):
        """Send data to statsd."""
        try:
            self._sock.sendto(data.encode('ascii'), self._addr)
        except (socket.error, RuntimeError):
            # No time for love, Dr. Jones!
            pass

    def pipeline(self):
        return Pipeline(self)


class TCPStatsClient(StatsClientBase):
    """TCP version of StatsClient."""

    def __init__(self, host='localhost', port=8125, prefix=None,
                 timeout=None, ipv6=False):
        """Create a new client."""
        self._host = host
        self._port = port
        self._ipv6 = ipv6
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None

    def _send(self, data):
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        self._do_send(data)

    def _do_send(self, data):
        self._sock.sendall(data.encode('ascii') + b'\n')

    def close(self):
        if self._sock and hasattr(self._sock, 'close'):
            self._sock.close()
        self._sock = None

    def connect(self):
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, fam, socket.SOCK_STREAM)[0]
        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(addr)

    def pipeline(self):
        return TCPPipeline(self)

    def reconnect(self, data):
        self.close()
        self.connect()


class PipelineBase(StatsClientBase):

    __metaclass__ = abc.ABCMeta

    def __init__(self, client):
        self._client = client
        self._prefix = client._prefix
        self._stats = deque()

    @abc.abstractmethod
    def _send(self):
        pass

    def _after(self, data):
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


class Pipeline(PipelineBase):

    def __init__(self, client):
        super(Pipeline, self).__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(data)
                data = stat
            else:
                data += '\n' + stat
        self._client._after(data)


class TCPPipeline(PipelineBase):

    def _send(self):
        self._client._after('\n'.join(self._stats))
        self._stats.clear()
