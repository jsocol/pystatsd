# Only including the async functionality in timer if on a Python version with coroutines
import sys

if sys.version_info >= (3, 5): # async/await syntax is only present on Py3.5+
    from .async_timer import AsyncTimer as Timer
else:
    from .base_timer import Timer