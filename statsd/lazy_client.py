class LazyClient(object):

    def __init__(self, use_django=True, use_env=True):
        self.use_django = use_django
        self.use_env = use_env

    def init_statsd(self):
        if self.use_django:
            from .defaults.django import statsd

        elif self.use_env:
            from .defaults.env import statsd

        self.statsd = statsd
        return statsd

    def __getattr__(self, value):
        statsd = self.__dict__.setdefault('statsd', self.init_statsd())
        fun = getattr(statsd, value)

        return fun
