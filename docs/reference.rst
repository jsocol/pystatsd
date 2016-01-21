.. _reference-chapter:

=============
API Reference
=============

The ``StatsClient`` provides accessors for all the types of data the
statsd_ server supports.

.. note::

    Each public stats API method supports a ``rate`` parameter, but
    statsd doesn't always use it the same way. See the
    :ref:`types-chapter` for more information.


.. _StatsClient:

``StatsClient``
===============

::

    StatsClient(host='localhost', port=8125, prefix=None, maxudpsize=512)

Create a new ``StatsClient`` instance with the appropriate connection
and prefix information.

* ``host``: the hostname or IPv4 address of the statsd_ server.

* ``port``: the port of the statsd server.

* ``prefix``: a prefix to distinguish and group stats from an
  application or environment.

* ``maxudpsize``: the largest safe UDP packet to save. 512 is generally
  considered safe for the public internet, but private networks may
  support larger packet sizes.


.. _incr:

``incr``
--------

::

    StatsClient().incr(stat, count=1, rate=1)

Increment a :ref:`counter <counter-type>`.

* ``stat``: the name of the counter to increment.

* ``count``: the amount to increment by. Typically an integer. May be
  negative, but see also :ref:`decr`.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server will take the sample
  rate into account for counters.


.. _decr:

``decr``
--------

::

    StatsClient().decr(stat, count=1, rate=1)

Decrement a :ref:`counter <counter-type>`.

* ``stat``: the name of the counter to decrement.

* ``count``: the amount to decrement by. Typically an integer. May be
  negative but that will have the impact of incrementing the counter.
  See also :ref:`incr`.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server will take the sample
  rate into account for counters.


.. _gauge:

``gauge``
---------

::

    StatsClient().gauge(stat, value, rate=1, delta=False)

Set a :ref:`gauge <gauge-type>` value.

* ``stat``: the name of the gauge to set.

* ``value``: the current value of the gauge.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server does *not* take the
  sample rate into account for gauges. Use with care.

* ``delta``: whether or not to consider this a delta value or an
  absolute value. See the :ref:`gauge <gauge-type>` type for more
  detail.

.. note::

   Gauges were added to the statsd server in commit 0ed78be_. If you try
   to use this method with an older version of the server, the data will
   not be recorded.


.. _set:

``set``
---------

::

    StatsClient().set(stat, value, rate=1)

Increment a :ref:`set <set-type>` value.

* ``stat``: the name of the set to update.

* ``value``: the unique value to count.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server does *not* take the
  sample rate into account for sets. Use with care.

.. note::

   Sets were added to the statsd server in commit 1c10cfc0ac_. If you
   try to use this method with an older version of the server, the
   data will not be recorded.


.. _timing:

``timing``
----------

::

    StatsClient().timing(stat, delta, rate=1)

Record :ref:`timer <timer-type>` information.

* ``stat``: the name of the timer to use.

* ``delta``: the number of milliseconds whatever action took. Should
  always be milliseconds.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server does *not* take the
  sample rate into account for timers.


.. _timer:

``timer``
=========

::

    with StatsClient().timer(stat, rate=1):
        pass

::

    @StatsClient().timer(stat, rate=1)
    def foo():
        pass

::

    timer = StatsClient().timer('foo', rate=1)

Automatically record timing information for a managed block or function
call.  See also the :ref:`chapter on timing <timing-chapter>`.

* ``stat``: the name of the timer to use.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server does *not* take the
  sample rate into account for timers.

.. _timer-start:

``start``
---------

::

    StatsClient().timer('foo').start()

Causes a timer object to start counting. Called automatically when the
object is used as a decorator or context manager. Returns the timer
object for simplicity.


.. _timer-stop:

``stop``
--------

::

    timer = StatsClient().timer('foo').start()
    timer.stop()

Causes the timer object to stop timing and send the results to statsd_.
Can be called with ``send=False`` to prevent immediate sending
immediately, and use ``send()``. Called automatically when the object is
used as a decorator or context manager. Returns the timer object.

If ``stop()`` is called before ``start()``, a ``RuntimeError`` is
raised.


.. _timer-send:

``send``
--------

::

    timer = StatsClient().timer('foo').start()
    timer.stop(send=False)
    timer.send()

Causes the timer to send any unsent data. If the data has already been
sent, or has not yet been recorded, a ``RuntimeError`` is raised.

.. note::
   See the note abbout :ref:`timer objects and pipelines <timer-direct-note>`.


.. _pipeline:

``pipeline``
============

::

    StatsClient().pipeline()

Returns a :ref:`Pipeline <pipeline-chapter>` object for collecting
several stats. Can also be used as a context manager::

    with StatsClient().pipeline() as pipe:
        pipe.incr('foo')


.. _pipeline-send:

``send``
--------

::

    pipe = StatsClient().pipeline()
    pipe.incr('foo')
    pipe.send()

Causes a :ref:`Pipeline <pipeline-chapter>` object to send all batched
stats.

.. note::

   This method is not implemented on the base StatsClient class.


.. _TCPStatsClient:

``TCPStatsClient``
==================

::

    TCPStatsClient(host='localhost', port=8125, prefix=None, timeout=None)

Create a new ``TCPStatsClient`` instance with the appropriate connection
and prefix information.

* ``host``: the hostname or IPv4 address of the statsd_ server.

* ``port``: the port of the statsd server.

* ``prefix``: a prefix to distinguish and group stats from an
  application or environment.

* ``timeout``: socket timeout for any actions on the connection socket.


``TCPStatsClient`` implements all methods of ``StatsClient``, including
``pipeline()``, with the difference that it is not thread safe and it
can raise exceptions on connection errors. Unlike ``StatsClient`` it
uses a TCP connection to communicate with StatsD.

In addition to the stats methods, ``TCPStatsClient`` supports the
following TCP-specific methods.


.. _tcp_close:

``close``
---------

::

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')
    statsd.close()

Closes a connection that's currently open and deletes it's socket. If
this is called on a ``TCPStatsClient`` which currently has no open
connection it is a non-action.


.. _tcp_connect:

``connect``
-----------

::

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')  # calls connect() internally
    statsd.close()
    statsd.connect()  # creates new connection

Creates a connection to StatsD. If there are errors like connection
timed out or connection refused, the according exceptions will be
raised. It is usually not necessary to call this method because sending
data to StatsD will call ``connect`` implicitely if the current instance
of ``TCPStatsClient`` does not already hold an open connection.


.. _tcp_reconnect:

``reconnect``
-------------

::

    from statsd import TCPStatsClient

    statsd = TCPStatsClient()
    statsd.incr('some.event')
    statsd.reconnect()  # closes open connection and creates new one

Closes a currently existing connection and replaces it with a new one.
If no connection exists already it will simply create a new one.
Internally this does nothing else than calling ``close()`` and
``connect()``.


.. _statsd: https://github.com/etsy/statsd
.. _0ed78be: https://github.com/etsy/statsd/commit/0ed78be7
.. _1c10cfc0ac: https://github.com/etsy/statsd/commit/1c10cfc0ac
