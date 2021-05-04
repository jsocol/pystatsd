======================
A Python statsd client
======================

A python client for [Etsy](http://etsy.com)'s [StatsD](https://github.com/etsy/statsd) server and [InfluxDB's](http://influxdb.com) [Telegraf](https://github.com/influxdb/telegraf) StatsD server.

.. image:: https://img.shields.io/pypi/v/statshog.svg
   :target: https://pypi.python.org/pypi/statshog/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/statshog.svg
   :target: https://pypi.python.org/pypi/statshog/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/wheel/statshog.svg
   :target: https://pypi.python.org/pypi/statshog/
   :alt: Wheel Status

:Code:          https://github.com/macobo/statshog
:License:       MIT; see LICENSE file
:Issues:        https://github.com/macobo/statshog/issues
:Documentation: https://statsd.readthedocs.io/

Quickly, to use:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats:

.. code-block:: python

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo')
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.


Installing
==========

The easiest way to install statsd is with pip!

You can install from PyPI::

    $ pip install statsd

Or GitHub::

    $ pip install -e git+https://github.com/macobo/statshog#egg=statshog

Or from source::

    $ git clone https://github.com/macobo/statshog
    $ cd pystatsd
    $ python setup.py install


To use together with [django-statsd](https://github.com/django-statsd/django-statsd), add the following to your `settings.py::

    STATSD_CLIENT = "statshog"


Docs
====

There are lots of docs in the ``docs/`` directory and on ReadTheDocs_.


.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
.. _ReadTheDocs: https://statsd.readthedocs.io/en/latest/index.html
