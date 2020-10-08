.. _reference-chapter:

=============
API Reference
=============

The ``StatsClient`` provides accessors for all the types of data the statsd_
server supports.

.. note::

    Each public stats API method supports a ``rate`` parameter, but statsd
    doesn't always use it the same way. See the :ref:`types-chapter` for more
    information.


.. py:class:: StatsClient(host='localhost', port=8125, prefix=None, maxudpsize=512)

    Create a new ``StatsClient`` instance with the appropriate connection and
    prefix information.

    :param str host: the hostname or IP address of the statsd_ server
    :param int port: the port of the statsd server
    :param prefix: a prefix to distinguish and group stats from an application
        or environment
    :type prefix: str or None
    :param int maxudpsize: the largest safe UDP packet to send. 512 is
        generally considered safe for the public internet, but private networks
        may support larger packet sizes.

.. py:method:: StatsClient.close()

    Close the underlying UDP socket.

.. py:method:: StatsClient.incr(stat, count=1, rate=1)

    Increment a :ref:`counter <counter-type>`.

    :param str stat: the name of the counter to increment
    :param int count: the amount to increment by. Typically an integer.  May be
        negative, but see also :py:meth:`decr() <StatsClient.decr()>`.
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server will take the
        sample rate into account for counters.

.. py:method:: StatsClient.decr(stat, count=1, rate=1)

    Decrement a :ref:`counter <counter-type>`.

    :param str stat: the name of the counter to increment
    :param int count: the amount to increment by. Typically an integer.  May be
        negative, but that will have the impact of incrementing the counter but
        see also :py:meth:`incr() <StatsClient.incr()>`.
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server will take the
        sample rate into account for counters

.. py:method:: StatsClient.gauge(stat, value, rate=1, delta=False)

    Set a :ref:`gauge <gauge-type>` value.

    :param str stat: the name of the gauge to set
    :param value: the current value of the gauge
    :type value: int or float
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server does *not* take the
        sample rate into account for gauges. Use with care
    :param bool delta: whether or not to consider this a delta value or an
        absolute value. See the :ref:`gauge <gauge-type>` type for more detail

.. note::

    Gauges were added to the statsd server in version 0.1.1.

.. note::

    Gauge deltas were added to the statsd server in version 0.6.0.

.. py:method:: StatsClient.set(stat, value, rate=1)

    Increment a :ref:`set <set-type>` value.

    :param str stat: the name of the set to update
    :param value: the unique value to count
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server does *not* take the
        sample rate into account for sets. Use with care.

.. note::

   Sets were added to the statsd server in version 0.6.0.

.. py:method:: StatsClient.timing(stat, delta, rate=1)

    Record :ref:`timer <timer-type>` information.

    :param str stat: the name of the timer to use
    :param delta: the number of milliseconds whatever action took.
        :py:class:`datetime.timedelta` objects will be converted to
        milliseconds
    :type delta: int or float or datetime.timedelta
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server does *not* take the
        sample rate into account for timers.

.. py:method:: StatsClient.timer(stat, rate=1)

    Return a :py:class:`Timer` object that can be used as a context manager or
    decorator to automatically record timing for a block or function call. See
    also the :ref:`chapter on timing <timing-chapter>`.

    :param str stat: the name of the timer to use
    :param float rate: a sample rate, a float between 0 and 1. Will only send
        data this percentage of the time. The statsd server does *not* take the
        sample rate into account for timers.

.. code-block:: python

    with StatsClient().timer(stat, rate=1):
        pass

    # or

    @StatsClient().timer(stat, rate=1)
    def foo():
        pass

    # or (see below for more Timer methods)

    timer = StatsClient().timer('foo', rate=1)

    with timer:
        pass

    @timer
    def bar():
        pass

.. py:method:: StatsClient.pipeline()

    Returns a :py:class:`Pipeline` object for collecting several stats.  Can
    also be used as a context manager.

.. code-block:: python

    pipe = StatsClient().pipeline()
    pipe.incr('foo')
    pipe.send()

    # or

    with StatsClient().pipeline as pipe:
        pipe.incr('bar')

.. py:class:: Timer()

    The :ref:`Timer objects <timer-object>` returned by
    :py:meth:`StatsClient.timer()`. These should never be instantiated
    directly.

:py:class:`Timer` objects should not be shared between threads (except when
used as decorators, which is thread-safe) but could be used within another
context manager or decorator. For example:

.. code-block:: python

    @contextmanager
    def my_context():
        timer = statsd.timer('my_context_timer')
        timer.start()
        try:
            yield
        finally:
            timer.stop()

:py:class:`Timer` objects may be reused by calling :py:meth:`start()
<Timer.start()>` again.

.. py:method:: Timer.start()

    Causes a timer object to start counting. Called automatically when the
    object is used as a decorator or context manager. Returns the timer object
    for simplicity.

.. py:method:: Timer.stop(send=True)

    Causes the timer object to stop timing and send the results to statsd_.
    Can be called with ``send=False`` to prevent immediate sending immediately,
    and use :py:meth:`send() <Timer.send()>`. Called automatically when the
    object is used as a decorator or context manager. Returns the timer object.

    If ``stop()`` is called before :py:meth:`start() <Timer.start()>`, a
    ``RuntimeError`` is raised.

    :param bool send: Whether to automatically send the results

.. code-block:: python

    timer = StatsClient().timer('foo').start()
    timer.stop()

.. py:method:: Timer.send()

    Causes the timer to send any unsent data. If the data has already been
    sent, or has not yet been recorded, a ``RuntimeError`` is raised.

.. code-block:: python

    timer = StatsClient().timer('foo').start()
    timer.stop(send=False)
    timer.send()

.. note::

    See the note abbout :ref:`timer objects and pipelines <timer-direct-note>`.

.. py:class:: Pipeline()

    A :ref:`Pipeline <pipeline-chapter>` object that can be used to collect and
    send several stats at once. Useful for reducing network traffic and
    speeding up instrumentation under certain loads. Can be used as a context
    manager.

    Pipeline extends :py:class:`StatsClient` and has all associated methods.

.. code-block:: python

    pipe = StatsClient().pipeline()
    pipe.incr('foo')
    pipe.send()

    # or

    with StatsClient().pipeline as pipe:
        pipe.incr('bar')

.. py:method:: Pipeline.send()

    Causes the :py:class:`Pipeline` object to send all batched stats in as few
    packets as possible.

.. py:class:: TCPStatsClient(host='localhost', port=8125, prefix=None, timeout=None, ipv6=False)

    Create a new ``TCPStatsClient`` instance with the appropriate connection
    and prefix information.

    :param str host: the hostname or IP address of the statsd_ server
    :param int port: the port of the statsd server
    :param prefix: a prefix to distinguish and group stats from an application
        or environment.
    :type prefix: str or None
    :param float timeout: socket timeout for any actions on the connection
        socket.

``TCPStatsClient`` implements all methods of :py:class:`StatsClient`, including
:py:meth:`pipeline() <StatsClient.pipeline>`, with the difference that it is
not thread safe and it can raise exceptions on connection errors. Unlike
:py:class:`StatsClient` it uses a TCP connection to communicate with StatsD.

In addition to the stats methods, ``TCPStatsClient`` supports the following
TCP-specific methods.

.. py:method:: TCPStatsClient.close()

    Closes a connection that's currently open and deletes it's socket. If this
    is called on a :py:class:`TCPStatsClient` which currently has no open
    connection it is a non-action.

.. code-block:: python

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')
    statsd.close()

.. py:method:: TCPStatsClient.connect()

    Creates a connection to StatsD. If there are errors like connection timed
    out or connection refused, the according exceptions will be raised. It is
    usually not necessary to call this method because sending data to StatsD
    will call ``connect`` implicitely if the current instance of
    :py:class:`TCPStatsClient` does not already hold an open connection.

.. code-block:: python

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')  # calls connect() internally
    statsd.close()
    statsd.connect()  # creates new connection

.. py:method:: TCPStatsClient.reconnect()

    Closes a currently existing connection and replaces it with a new one.  If
    no connection exists already it will simply create a new one.  Internally
    this does nothing else than calling :py:meth:`close()
    <TCPStatsClient.close()>` and :py:meth:`connect()
    <TCPStatsClient.connect()>`.

.. code-block:: python

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')
    statsd.reconnect()  # closes open connection and creates new one

.. py:class:: UnixSocketStatsClient(socket_path, prefix=None, timeout=None)

    A version of :py:class:`StatsClient` that communicates over Unix sockets.
    It implements all methods of :py:class:`StatsClient`.

    :param str socket_path: the path to the (writeable) Unix socket
    :param prefix: a prefix to distinguish and group stats from an application
        or environment
    :type prefix: str or None
    :param float timeout: socket timeout for any actions on the connection
        socket.


.. _statsd: https://github.com/etsy/statsd
