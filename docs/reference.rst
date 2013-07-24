.. _reference-chapter:

=============
API Reference
=============

The ``StatsClient`` provides accessors for all the types of data the
statsd_ server supports.

.. note::

    Each public API method supports a ``rate`` parameter, but statsd
    doesn't always use it the same way. See the :ref:`types-chapter` for
    more information.


.. _StatsClient:

``StatsClient``
===============

::

    StatsClient(host='localhost', port=8125, prefix=None)

Create a new ``StatsClient`` instance with the appropriate connection
and prefix information.

* ``host``: the hostname or IPv4 address of the statsd_ server.

* ``port``: the port of the statsd server.

* ``prefix``: a prefix to distinguish and group stats from an
  application or environment.


.. _incr:

``incr``
========

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
========

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


.. _timing:

``timing``
==========

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

Automatically record timing information for a managed block or function
call.  See also the :ref:`chapter on timing <timing-chapter>`.

* ``stat``: the name of the timer to use.

* ``rate``: a sample rate, a float between 0 and 1. Will only send data
  this percentage of the time. The statsd server does *not* take the
  sample rate into account for timers.


.. _gauge:

``gauge``
=========

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
=========

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
========

::

    pipe = StatsClient().pipeline()
    pipe.incr('foo')
    pipe.send()

Causes a :ref:`Pipeline <pipeline-chapter>` object to send all batched
stats.

.. note::

   This method is not implemented on the base StatsClient class.


.. _statsd: https://github.com/etsy/statsd
.. _0ed78be: https://github.com/etsy/statsd/commit/0ed78be7
