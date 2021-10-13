from __future__ import absolute_import, division, unicode_literals

import threading
from collections import deque
try:
    from Queue import Queue, Full # Python 2
except ImportError:
    from queue import Queue, Full # Python 3

from .base import StatsClientBase, PipelineBase


class CLOSE(object):
    pass


class Pipeline(PipelineBase):
    def _send(self):
        self._client._send(self._stats)
        # Clearing the deque by making a new one: we only want the thread to send
        # stats that exist in the queue as of right now, not those that might be
        # added to this pipeline before the thread picks up the _stats deque we just
        # sent it:
        self._client._stats = deque()


class ThreadStatsClient(StatsClientBase):
    def __init__(self, client, prefix=None, queue_size=1000, no_fail=True, daemon=False):
        self._prefix = prefix
        self._client = client # The StatsClient instance we're wrapping.
        self._client_pipeline = client.pipeline()

        self._no_fail = no_fail
        self._queue = Queue(maxsize=queue_size) # Don't allow too much data to be
            # buffered or we could grow unbounded and use all the memory.
        self._thread = threading.Thread(target=self._background_thread)
        self._thread.daemon = daemon
        self._thread.start()

    def _send(self, data):
        try:
            self._queue.put(data, block=False)
        except Full:
            if self._no_fail:
                # No time for love, Dr. Jones!
                pass
            else:
                raise

    def close(self):
        self._queue.put(CLOSE)
        self._thread.join()

    def _background_thread(self):
        while True:
            data = self._queue.get()
            if data == CLOSE:
                self._client.close()
                break
            elif isinstance(data, deque):
                # We got a pipeline's data, using the wrapped client's pipeline to send:
                self._client_pipeline._stats = data
                self._client_pipeline._send()
            else:
                self._client._send(data)

    def pipeline(self):
        return Pipeline(self)
