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

You can also add a prefix to all your stats::

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.


In Django
=========

If you're lucky enough to be using statsd in Django, you can configure a
default client in your settings module with two values. The defaults are::

    STATSD_HOST = 'localhost'
    STATSD_PORT = 8125

Then instead of instantiating a new client every time, you can just grab::

    >>> from statsd import statsd
    >>> statsd.incr('foo')

You can even set a prefix (optionally)::

    STATSD_PREFIX = 'foo'

This can help differentiate between environments, like dev, staging, and
production.


Context Manager
===============

You can use a ``StatsClient`` instance as a context manager to easily time
sections of code with the ``timer()`` method::

    >>> from statsd import statsd
    >>> with statsd.timer('bar'):
    ...     func()
    ...     func()

When the managed block exits, the client will automatically send the time it
took to statsd.

If you'd like to catpure the elapsed time, add a variable to the ``with``
block::

    >>> from statsd import statsd
    >>> with statsd.timer('bar') as timer:
    ...     func()
    >>> print timer.ms  # Elapsed time in milliseconds.


Decorator
=========

You can *also* use a ``StatsClient`` instance as a decorator, also with the
``timer()`` method::

    >>> from statsd import statsd
    >>> @statsd.timer('bar')
    ... def foo():
    ...     pass

Every time ``foo()`` is called, timing information will be sent to the stat
``bar``.


Sample Rates
============

All methods support an optional ``rate`` (kw)arg. This is a float between 0 and
1 that specifies what fraction of data to send through (for a specific call).
Sample rates are recorded by statsd.

For example, here ``foo`` will be incremented approximately 50% of the time::

    >>> from statsd import statsd
    >>> statsd.incr('foo', 1, rate=0.5)

Statsd understands that this is a 50% sample rate and will adjust accordingly.

Similarly with ``decr()`` and timings::

    >>> from statsd import statsd
    >>> statsd.decr('foo', 1, rate=0.5)
    >>> statsd.timing('foo', 320, rate=0.25)
    >>> with statsd.timer('bar', rate=0.1):
    ...    pass
    >>> @statsd.timer('bar', rate=0.5)
    ... def foo():
    ...     pass
