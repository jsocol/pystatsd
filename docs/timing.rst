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
it manually, using the :py:meth:`StatsClient.timing()` method:

.. code-block:: python

    import time
    from datetime import datetime
    from statsd import StatsClient

    statsd = StatsClient()

    # Pass milliseconds directly

    start = time.time()
    time.sleep(3)
    # You must convert to milliseconds:
    dt = int((time.time() - start) * 1000)
    statsd.timing('slept', dt)

    # Or pass a timedelta

    start = datetime.utcnow()
    time.sleep(3)
    dt = datetime.utcnow() - start
    statsd.timing('slept', dt)


.. _timer-context-manager:

Using a context manager
=======================

The :py:meth:`StatsClient.timer()` method will return a :py:class:`Timer`
object that can be used as both a context manager and a thread-safe decorator.

When used as a context manager, it will automatically report the time taken for
the inner block:

.. code-block:: python

    from statsd import StatsClient

    statsd = StatsClient()

    with statsd.timer('foo'):
        # This block will be timed.
        for i in xrange(0, 100000):
            i ** 2
    # The timing is sent immediately when the managed block exits.


.. _timer-decorator:

Using a decorator
=================

:py:class:`Timer` objects can be used to decorate a method in a thread-safe
manner.  Every time the decorated function is called, the time it took to
execute will be sent to the statsd server.

.. code-block:: python

    from statsd import StatsClient

    statsd = StatsClient()

    @statsd.timer('myfunc')
    def myfunc(a, b):
        """Calculate the most complicated thing a and b can do."""

    # Timing information will be sent every time the function is called.
    myfunc(1, 2)
    myfunc(3, 7)



.. _timer-object:

Using a Timer object directly
=============================

.. versionadded:: 2.1

:py:class:`Timer` objects function as context managers and as decorators, but
they can also be used directly. (Flat is, after all, better than nested.)

.. code-block:: python

    from statsd import StatsClient

    statsd = StatsClient()

    foo_timer = statsd.timer('foo')
    foo_timer.start()
    # Do something fun.
    foo_timer.stop()

When :py:meth:`Timer.stop()` is called, a :ref:`timing stat <timer-type>` will
automatically be sent to StatsD. You can over ride this behavior with the
``send=False`` keyword argument to :py:meth:`stop() <Timer.stop()>`:

.. code-block:: python

    foo_timer.stop(send=False)
    foo_timer.send()

Use :py:meth:`Timer.send()` to send the stat when you're ready.

.. _timer-direct-note:

.. note::

    This use of timers is compatible with :ref:`Pipelines <pipeline-chapter>`
    but the ``send()`` method may not behave exactly as expected. Timing data
    *must* be sent, either by calling ``stop()`` without ``send=False`` or
    calling ``send()`` explicitly, in order for it to be included in the
    pipeline. However, it will *not* be sent immediately.

    .. code-block:: python

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

        with statsd.pipeline() as pipe:
            foo_timer = pipe.timer('foo').start()
            pipe.incr('bar')
            # Do something...
            foo_timer.stop(send=False)  # Data will _not_ be sent
