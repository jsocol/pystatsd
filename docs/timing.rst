.. _timing-chapter:

============
Using Timers
============

:ref:`Timers <timers>` are an incredibly powerful tool for tracking application
performance. Statsd provides a number of ways to use them to instrument your
code.


Calling ``timing`` manually
===========================

The simplest way to use a timer is to record the time yourself and send it
manually, using the :ref:`timing` method::

    import time
    from statsd import StatsClient

    statsd = StatsClient()

    start = time.time()
    time.sleep(3)

    # You must convert to milliseconds:
    dt = int((time.time() - start) * 1000)
    statsd.timing('slept', dt)


Using a context manager
=======================

Each ``StatsClient`` instance contains a :ref:`timer` attribute that can be
used as a context manager or a decorator. When used as a context manager, it
will automatically report the time taken for the inner block::

    from statsd import StatsClient

    statsd = StatsClient()

    with stats.timer('foo'):
        # This block will be timed.
        for i in xrange(0, 100000):
            i ** 2
    # The timing is sent immediately when the managed block exits.


Using a decorator
=================

The ``timer`` attribute can also be used as a function decorator. Every time
the decorated function is called, the time it took to execute will be sent to
the statsd server.

::

    from statsd import StatsClient

    statsd = StatsClient()

    @statsd.timer('myfunc')
    def myfunc(a, b):
        """Calculate the most complicated thing a and b can do."""

    # Timing information will be sent every time the function is called.
    myfunc(1, 2)
    myfunc(3, 7)
