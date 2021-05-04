from __future__ import absolute_import

from .client import StatsClient
from .client import TCPStatsClient
from .client import UnixSocketStatsClient


__version__ = "0.0.1"
VERSION = [int(x) for x in __version__.split('.')]
__all__ = ["StatsClient", "TCPStatsClient", "UnixSocketStatsClient"]
