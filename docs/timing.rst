.. _timing-chapter:

============
Using Timers
============

:ref:`Timers <timer-type>` are an incredibly powerful tool for tracking
application performance. Statsd provides a number of ways to use them to
instrument your code.

There are four ways to use timers.


Calling ``timing`` manually
===========================

The simplest way to use a timer is to record the time yourself and send
it manually, using the :ref:`timing` method::

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

Each ``StatsClient`` instance contains a :ref:`timer` attribute that can
be used as a context manager or a decorator. When used as a context
manager, it will automatically report the time taken for the inner
block::

    from statsd import StatsClient

    statsd = StatsClient()

    with statsd.timer('foo'):
        # This block will be timed.
        for i in xrange(0, 100000):
            i ** 2
    # The timing is sent immediately when the managed block exits.


Using a decorator
=================

The ``timer`` attribute decorates your methods in a thread-safe manner.
Every time the decorated function is called, the time it took to execute
will be sent to the statsd server.

::

    from statsd import StatsClient

    statsd = StatsClient()

    @statsd.timer('myfunc')
    def myfunc(a, b):
        """Calculate the most complicated thing a and b can do."""

    # Timing information will be sent every time the function is called.
    myfunc(1, 2)
    myfunc(3, 7)



Using a Timer object directly
=============================

.. versionadded:: 2.1

:py:class:`statsd.client.Timer` objects function as context managers and
as decorators, but they can also be used directly. (Flat is, after all,
better than nested.)

::

    from statsd import StatsClient

    statsd = StatsClient()

    foo_timer = statsd.timer('foo')
    foo_timer.start()
    # Do something fun.
    foo_timer.stop()

When :py:meth:`statsd.client.Timer.stop` is called, a :ref:`timing stat
<timer-type>`_ will automatically be sent to StatsD. You can over ride
this behavior with the ``send=False`` keyword argument to ``stop()``::

    foo_timer.stop(send=False)
    foo_timer.send()

Use :py:meth:`statsd.client.Timer.send` to send the stat when you're
ready.

.. _timer-direct-note:

.. note::
   This use of timers is compatible with :ref:`Pipelines
   <pipeline-chapter>`_ but be careful with the ``send()`` method. It
   *must* be called for the stat to be included when the Pipeline
   finally sends data, but ``send()`` will *not* immediately cause data
   to be sent in the context of a Pipeline. For example::

    with statsd.pipeline() as pipe:
        foo_timer = pipe.timer('foo').start()
        # Do something...
        pipe.incr('bar')
        foo_timer.stop()  # Will be sent when the managed block exits.

    with statsd.pipeline() as pipe:
        foo_timer = pipe.timer('foo').start()
        # Do something...
        pipe.incr('bar')
        foo_timer.stop(send=False)  # Will not be sent.
        foo_timer.send()  # Will be sent when the managed block exits.
        # Do something else...
