from inspect import iscoroutinefunction
from .base_timer import Timer, time_now, safe_wraps

class AsyncTimer(Timer):
    def __call__(self, f):
        if iscoroutinefunction(f):
            @safe_wraps(f)
            async def _wrapped(*args, **kwargs):
                start_time = time_now()
                try:
                    return await f(*args, **kwargs)
                finally:
                    elapsed_time_ms = 1000.0 * (time_now() - start_time)
                    self.client.timing(self.stat, elapsed_time_ms, self.rate)
            return _wrapped
        else:
            return super().__call__(f)