.. Python StatsD documentation master file, created by
   sphinx-quickstart on Mon Apr  9 15:47:23 2012.
   You can adapt this file completely to your liking, but it should at
   least contain the root `toctree` directive.

Welcome to Python StatsD's documentation!
=========================================

statsd_ is a friendly front-end to Graphite_. This is a Python client
for the statsd daemon, with added support for tags (as defined in the
Datadog protocol extension).

Forked from https://github.com/jsocol/pystatsd.

.. image:: https://travis-ci.org/jsocol/pystatsd.png?branch=master
   :target: https://travis-ci.org/jsocol/pystatsd
   :alt: Travis-CI build status

.. image:: https://pypip.in/v/statsd/badge.png
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Latest release

.. image:: https://pypip.in/d/statsd/badge.png
   :target: https://pypi.python.org/pypi/statsd/
   :alt: Downloads

:Code:          https://github.com/jsocol/pystatsd
:License:       MIT; see LICENSE file
:Issues:        https://github.com/jsocol/pystatsd/issues
:Documentation: https://statsd.readthedocs.io/

Quickly, to use:

.. code-block:: pycon

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125)
    >>> c.incr('foo')  # Increment the 'foo' counter.
    >>> c.timing('stats.timed', 320)  # Record a 320ms 'stats.timed'.

You can also add a prefix to all your stats:

.. code-block:: pycon

    >>> import statsd
    >>> c = statsd.StatsClient('localhost', 8125, prefix='foo',
    ... tags={'environment:production'})
    >>> c.incr('bar')  # Will be 'foo.bar' in statsd/graphite.


Installing
----------

The easiest way to install statsd is with pip!

You can install from PyPI:

.. code-block:: bash

    $ pip install statsd

Or GitHub:

.. code-block:: bash

    $ pip install -e git+https://github.com/jsocol/pystatsd#egg=statsd

Or from source:

.. code-block:: bash

    $ git clone https://github.com/jsocol/pystatsd
    $ cd statsd
    $ python setup.py install


Contents
--------

.. toctree::
   :maxdepth: 2

   configure.rst
   types.rst
   timing.rst
   pipeline.rst
   tcp.rst
   unix_socket.rst
   reference.rst
   contributing.rst


Indices and tables
------------------

* :ref:`search`

.. _statsd: https://github.com/etsy/statsd
.. _Graphite: https://graphite.readthedocs.io/
