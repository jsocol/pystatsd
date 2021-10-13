.. _thread-client-chapter:

=====================
Async
=====================


Timing async functions.
===========================

Timers work with async functions automatically by `await`ing them. See :ref:`Using Timers <using-a-decorator>`.

ThreadStatsClient
===========================

Both the UDP and TCP StatsClients perform potentially-blocking network operations so likely aren't suitable for using
alongside an event loop (although UDP is generally non-blocking so might meet your needs just fine). To safely
records stats in asynchronous code, a thread-based StatsClient is provided. This wraps another StatsClient and
uses a single background thread for the network operations.

.. code-block:: python

    from statsd import StatsClient, ThreadStatsClient

    statsd = ThreadStatsClient(client=StatsClient())

    # Send stats like normal, in sync or async code:

    @statsd.timer('async_func')
    async def async_func():
        """Do something asynchronously"""


    @statsd.timer('synchronous_func')
    def synchronous_func():
        """Do something quick logic"""

    async def main():
        synchronous_func()
        await async_func()
        statsd.incr("main")

    import trio
    trio.run(main)

    statsd.close() # Make sure to flush the queue and stop the thread


* The ``queue_size`` parameter controls how many metrics can queue up. Default is 1000.

* The ``no_fail`` parameter controls whether a full queue raises an exception (`True`: default) or simply drops the metric (specify `False`).

* The ``daemon`` parameter can be used to put the background thread in daemon mode so you don't have to remember to close it. This will prevent
the background thread from keeping the application running when the main thread returns. The cost is that any metrics still in the queue will be lost. This is only suitable ex. for long-running services where that's not a concern.