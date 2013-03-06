.. _pipeline-chapter:

=========
Pipelines
=========

The ``Pipeline`` class is a subclass of ``StatsClient`` that batches
together several stats before sending. It implements the entire client
interface, plus a ``send()`` method.

``Pipeline`` objects should be created with
``StatsClient().pipeline()``::

    client = StatsClient()

    pipe = client.pipeline()
    pipe.incr('foo')
    pipe.decr('bar')
    pipe.timing('baz', 520)
    pipe.send()

No stats will be sent until ``send()`` is called, at which point they
will be packed into as few UDP packets as possible.


As a Context Manager
====================

``Pipeline`` objects can also be used as context managers::

    with StatsClient().pipeline() as pipe:
        pipe.incr('foo')
        pipe.decr('bar')

``pipe.send()`` will be called automatically when the managed block
exits.


Thread Safety
=============

While ``StatsClient`` instances are considered thread-safe (or at least
as thread-safe as the standard library's ``socket.send`` is),
``Pipeline`` instances **are not thread-safe**. Storing stats for later
creates at least two important race conditions in a multi-threaded
environment. You should create one ``Pipeline`` per-thread, if
necessary.
