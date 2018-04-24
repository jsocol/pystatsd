======================
A Python statsd client
======================

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon, with added support for tags (as defined in the
Datadog protocol extension).

Forked from https://github.com/jsocol/pystatsd.

Quickly, to use:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix or tags to all your stats:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo',
    ... tags={'environment:production'}
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.


Installing
==========

The easiest way to install statsd is with pip!

From GitHub::

    $ pip install -e git+https://github.com/jsocol/pystatsd#egg=statsd

Or from source::

    $ git clone https://github.com/jsocol/pystatsd
    $ cd pystatsd
    $ python setup.py install


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
.. _ReadTheDocs: https://statsd.readthedocs.io/en/latest/index.html
