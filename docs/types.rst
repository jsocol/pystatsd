.. _types-chapter:

==========
Data Types
==========

The statsd_ server supports a number of different data types, and
performs different aggregation on each of them. The three main types are
*counters*, *timers*, and *gauges*.

The statsd server collects and aggregates in 30 second intervals before
flushing to Graphite_. Graphite usually stores the most recent data in
1-minute averaged buckets, so when you're looking at a graph, for each
stat you are typically seeing the average value over that minute.


.. _counter-type:

Counters
========

*Counters* are the most basic and default type. They are treated as a
count of a type of event per second, and are, in Graphite_, typically
averaged over one minute. That is, when looking at a graph, you are
usually seeing the average number of events per second during a
one-minute period.

The statsd server collects counters under the ``stats`` prefix.

Counters are managed with the :ref:`incr` and :ref:`decr` methods of
``StatsClient``::

    from statsd import StatsClient

    statsd = StatsClient()

    statsd.incr('some.event')

You can increment a counter by more than one by passing a second
parameter::

    statsd.incr('some.other.event', 10)

You can also use the ``rate`` parameter to produce sampled data. The
statsd server will take the sample rate into account, and the
``StatsClient`` will only send data ``rate`` percent of the time. This
can help the statsd server stay responsive with extremely busy
applications.

``rate`` is a float between 0 and 1::

    # Increment this counter 10% of the time.
    statsd.incr('some.third.event', rate=0.1)

Because the statsd server is aware of the sampling, it will still show
you the true average rate per second.

You can also decrement counters. The ``decr`` method takes the same
arguments as ``incr``::

    statsd.decr('some.other.event')
    # Decrease the counter by 5, 15% sample.
    statsd.decr('some.third.event', 5, rate=0.15)


.. _timer-type:

Timers
======

*Timers* are meant to track how long something took. They are an
invaluable tool for tracking application performance.

The statsd server collects all timers under the ``stats.timers`` prefix,
and will calculate the lower bound, mean, 90th percentile, upper bound,
and count of each timer for each period (by the time you see it in
Graphite, that's usually per minute).

* The *lower bound* is the lowest value statsd saw for that stat during
  that time period.

* The *mean* is the average of all values statsd saw for that stat 
  during that time period.

* The *90th percentile* is a value *x* such that 90% of all the values
  statsd saw for that stat during that time period are below *x*, and
  10% are above.  This is a great number to try to optimize.

* The *upper bound* is the highest value statsd saw for that stat during
  that time period.

* The *count* is the number of timings statsd saw for that stat during
  that time period. It is not averaged.

The statsd server only operates in millisecond timings. Everything
should be converted to milliseconds.

The ``rate`` parameter will sample the data being sent to the statsd
server, but in this case it doesn't make sense for the statsd server to
take it into account (except possibly for the *count* value, but then it
would be lying about how much data it averaged).

See the :ref:`timing documentation <timing-chapter>` for more detail on
using timers with Statsd.


.. _gauge-type:

Gauges
======

*Gauges* are a constant data type. They are not subject to averaging,
and they don't change unless you change them. That is, once you set a
gauge value, it will be a flat line on the graph until you change it
again.

Gauges are useful for things that are already averaged, or don't need to
reset periodically. System load, for example, could be graphed with a
gauge. You might use ``incr`` to count the number of logins to a system,
but a gauge to track how many active WebSocket connections you have.

The statsd server collects gauges under the ``stats.gauges`` prefix.

The :ref:`gauge` method also support the ``rate`` parameter to sample
data back to the statsd server, but use it with care, especially with
gauges that may not be updated very often.


Gauge Deltas
------------

Gauges may be *updated* (as opposed to *set*) by setting the ``delta``
keyword argument to ``True``. For example::

    statsd.gauge('foo', 70)  # Set the 'foo' gauge to 70.
    statsd.gauge('foo', 1, delta=True)  # Set 'foo' to 71.
    statsd.gauge('foo', -3, delta=True)  # Set 'foo' to 68.

.. note::

   Support for gauge deltas was added to the server in 3eecd18_. You
   will need to be running at least that version for the ``delta`` kwarg
   to have any effect.


.. _set-type:

Sets
======

*Sets* count the number of unique values passed to a key.

For example, you could count the number of users accessing your system
using:

    statsd.set('users', userid)

If that method is called multiple times with the same userid in the
same sample period, that userid will only be counted once.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io
.. _3eecd18: https://github.com/etsy/statsd/commit/3eecd18
