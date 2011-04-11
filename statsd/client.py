import random
import socket


class StatsClient(object):
    """A client for statsd."""
    def __init__(self, host='localhost', port=8125):
        """Create a new client."""
        self._addr = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def timing(self, stat, time, rate=1):
        """Send new timing information. `time` is in milliseconds."""
        self._send(stat, '%d|ms' % time, rate)

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

        try:
            self._sock.sendto('%s:%s' % (stat, value), self._addr)
        except socket.error:
            # No time for love, Dr. Jones!
            pass
