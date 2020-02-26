.. _tags-chapter:

============================
Unsupported: Tagging Metrics
============================

Tagged metrics—such as those used by Datadog_ and `Telegraf`_—are
explicitly outside the scope of this library. Alternatives_ exist and
are recommended. This document lays out the reasons to avoid support for
tags.


Aggregating and Disaggregating Metrics
======================================

Given a simple metric, like a :ref:`counter <counter-type>` or
:ref:`timer-type`, the very first operation StatsD will perform is an
aggregation over time. For example, over a 30-second window, calculate
the total number of events (a counter) or several aggregations like
average, median, 90th percentile (a timer).

A very common next step is for users to want to perform additional
aggregations. For example, if we're timing a ``/widgets`` API endpoint
for both ``GET`` and ``POST`` requests, we might want to know the median
time across both HTTP methods.

*Without* tags, we must start with the most disaggregated metrics,
e.g.::

    statsd.timing('api.widgets.GET', response_time)
    statsd.timing('api.widgets.POST', response_time)

We can then *aggregate* these metrics with wildcards (e.g. in
Graphite)::

    weightedAverage(api.widgets.*.mean, api.widgets.*.count)

However, *with* tags, we have an alternative approach: to use a single,
aggregated metric name, and *disaggregate* via tags, e.g.::

    statsd.timing('api.widgets', response_time, {'method': 'GET'})
    statsd.timing('api.widgets', response_time, {'method': 'POST'})

By default, queries for the ``api.widgets`` timer will include all
requests, but may be filtered to specific subsets with tags (e.g. in
Datadog)::

    api.widgets.mean{method:GET}


Naming Metrics
==============

The examples above demonstrate that there is a fundamental change in how
metrics must be named, particularly in the absence of tags, to avoid
data loss. If tags are not supported, there is no way to disaggregate
``api.widgets`` into its ``GET`` and ``POST`` subsets.

Thus, it is incredibly important that an application be written with
specific metrics capabilities in mind. If using a metrics system that
does not support tags, like StatsD_ or StatsDaemon_, metric names must
be disaggregated by default. If using a system that *does* support tags,
like Datadog or Telegraf, metric names may be aggregated by default.

If an application is expecting tags to work but they are not supported
by the underlying metrics system, the best case scenario is a loss of
data resolution. The worst case scenario is a complete loss of data, if
the metrics system is incapable of correctly parsing the extended metric
data.


Explicit Opt-in
===============

Given that the best case scenario for a mismatch of application and
metrics system is a form of data loss, the choice to use metrics with
tags must be incredibly explicit.

Technically, this library is capable of sending metrics to Datadog_ and
Telegraf_, as well as StatsD_. However, to take advantage of these,
you'll need to change your strategy for naming—and tagging—metrics.

To avoid silently failing, this library forces you to make an explicit
change to how you send metrics to these systems. At a minimum, you must
touch every file that has ``import statsd``, but that's not really
enough: you need to touch every metrics call.


.. _Datadog: https://www.datadoghq.com/
.. _Telegraf: https://github.com/influxdata/telegraf
.. _Alternatives: https://pypi.org/project/statsd-tags/
.. _StatsD: https://github.com/etsy/statsd
.. _StatsDaemon: https://github.com/bitly/statsdaemon
