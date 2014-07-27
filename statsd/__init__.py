from __future__ import absolute_import

from .client import StatsClient


VERSION = (3, 0, 1)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['StatsClient']
