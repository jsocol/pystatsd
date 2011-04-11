======================
A Python statsd client
======================

`statsd <https://github.com/etsy/statsd>`_ is a friendly front-end to `Graphite
<http://graphite.wikidot.com/>`_. This is a Python client for the statsd
daemon.

To use::

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.


In Django
=========

If you're lucky enough to be using statsd in Django, you can configure a
default client in your settings module with two values. The defaults are::

    STATSD_HOST = 'localhost'
    STATSD_PORT = 8125

Then instead of instantiating a new client every time, you can just grab::

    >>> from statsd import statsd
    >>> statsd.incr('foo')
