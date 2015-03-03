from __future__ import with_statement
import abc
from collections import deque
from functools import wraps
import threading
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
        self._sent = False
        self._start_time = None

    def __call__(self, f):
        """Thread-safe timing function decorator."""
        @wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time.time()
            try:
                return_value = f(*args, **kwargs)
            finally:
                elapsed_time_ms = int(round(1000 * (time.time() - start_time)))
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
        self._start_time = time.time()
        return self

    def stop(self, send=True):
        if self._start_time is None:
            raise RuntimeError('Timer has not started.')
        dt = time.time() - self._start_time
        self.ms = int(round(1000 * dt))  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self):
        if self.ms is None:
            raise RuntimeError('No data recorded.')
        if self._sent:
            raise RuntimeError('Already sent data.')
        self._sent = True
        self.client.timing(self.stat, self.ms, self.rate)


class ConnHandlerBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port, fail_silently, timeout=None):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._fail_silently = fail_silently

    def send(self, data):
        try:
            self._send(data)
        except socket.error:
            if not self._fail_silently:
                raise

    @abc.abstractmethod
    def _send(self, data):
        pass


class ConnHandlerTCP(ConnHandlerBase):

    def __init__(self, *args, **kwargs):
        super(ConnHandlerTCP, self).__init__(*args, **kwargs)
        self._tlocal = threading.local()
        self._tlocal.sock = None

    def _send(self, data):
        if not self._tlocal.sock:
            self._connect()
        try:
            self._do_send(data)
        except socket.error:
            # try reconnecting and resending only once, so connections that
            # have been up but died in the mean time will get re-established
            self._reconnect_send(data)

    def _reconnect_send(self, data):
        self._close()
        self._connect()
        self._do_send(data)

    def _connect(self):
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, 0, socket.SOCK_STREAM)[0]
        self._tlocal.sock = socket.socket(family, socket.SOCK_STREAM)
        self._tlocal.sock.settimeout(self._timeout)
        self._tlocal.sock.connect(addr)

    def _do_send(self, data):
        self._tlocal.sock.sendall(data.encode('ascii'))

    def _close(self):
        if self._tlocal.sock and hasattr(self._tlocal.sock, 'close'):
            self._tlocal.sock.close()
        self._tlocal.sock = None


class ConnHandlerUDP(ConnHandlerBase):

    def __init__(self, *args, **kwargs):
        super(ConnHandlerUDP, self).__init__(*args, **kwargs)
        family, _, _, _, self._addr = socket.getaddrinfo(
            self._host, self._port, 0, socket.SOCK_DGRAM)[0]
        self._sock = socket.socket(family, socket.SOCK_DGRAM)

    def _send(self, data):
        self._sock.sendto(data.encode('ascii'), self._addr)


class StatsClient(object):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None,
                 maxudpsize=512, proto='udp', fail_silently=True,
                 timeout=None):
        """Create a new client."""
        self._conn_handlers = {
            'udp': ConnHandlerUDP,
            'tcp': ConnHandlerTCP,
        }
        if proto not in self._conn_handlers:
            raise RuntimeError('Parameter "proto" must be one of {0}.'
                               .format(', '.join(self._conn_handlers.keys())))
        self._conn_handler = self._conn_handlers[proto](
            host, port, fail_silently, timeout)
        self._prefix = prefix
        self._maxudpsize = maxudpsize

    def pipeline(self):
        return Pipeline(self)

    def timer(self, stat, rate=1):
        return Timer(self, stat, rate)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        self._send_stat(stat, '%d|ms' % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        self._send_stat(stat, '%s|c' % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1, delta=False):
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

    def set(self, stat, value, rate=1):
        """Set a set value."""
        self._send_stat(stat, '%s|s' % value, rate)

    def _send_stat(self, stat, value, rate):
        self._after(self._prepare(stat, value, rate))

    def _prepare(self, stat, value, rate):
        if rate < 1:
            if random.random() > rate:
                return
            value = '%s|@%s' % (value, rate)

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        return '%s:%s' % (stat, value)

    def _after(self, data):
        if data:
            self._send(data)

    def _send(self, data):
        """Send data to statsd using the according method."""
        self._conn_handler.send(data)


class Pipeline(StatsClient):
    def __init__(self, client):
        self._client = client
        self._prefix = client._prefix
        self._maxudpsize = client._maxudpsize
        self._stats = deque()

    def _after(self, data):
        if data is not None:
            self._stats.append(data)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        self.send()

    def send(self):
        # Use popleft to preserve the order of the stats.
        if not self._stats:
            return
        data = self._stats.popleft()
        while self._stats:
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(data)
                data = stat
            else:
                data += '\n' + stat
        self._client._after(data)
