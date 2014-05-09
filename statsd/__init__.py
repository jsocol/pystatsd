from __future__ import absolute_import

from .client import StatsClient


VERSION = (2, 1, 2)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['StatsClient']
