.. _pipeline-chapter:

=========
Pipelines
=========

The :py:class:`Pipeline` class is a subclass of :py:class:`StatsClient` that
batches together several stats before sending. It implements the entire client
interface, plus a :py:meth:`send() <Pipeline.send()>` method.

:py:class:`Pipeline` objects should be created with
:py:meth:`StatsClient.pipeline()`:

.. code-block:: python

    client = StatsClient()

    pipe = client.pipeline()
    pipe.incr('foo')
    pipe.decr('bar')
    pipe.timing('baz', 520)
    pipe.send()

No stats will be sent until :py:meth:`send() <Pipeline.send()>` is called, at
which point they will be packed into as few UDP packets as possible.


As a Context Manager
====================

:py:class:`Pipeline` objects can also be used as context managers:

.. code-block:: python

    with StatsClient().pipeline() as pipe:
        pipe.incr('foo')
        pipe.decr('bar')

:py:meth:`Pipeline.send()` will be called automatically when the managed block
exits.


Thread Safety
=============

While :py:class:`StatsClient` instances are considered thread-safe (or at least
as thread-safe as the standard library's ``socket.send`` is),
:py:class:`Pipeline` instances **are not thread-safe**. Storing stats for later
creates at least two important race conditions in a multi-threaded environment.
You should create one :py:class:`Pipeline` per-thread, if necessary.
