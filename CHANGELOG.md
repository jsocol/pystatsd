# Statsd Changelog

## UNRELEASED

## v4.0.1

### Fixed

- Updated PyPI trove classifiers for current Python versions.

## v4.0

### Added

- Updates support to Python 3.7 through 3.11.
- Added `close()` method to UDP-based `StatsClient`. (#136)

### Dropped

- Drops support for Python 2.

### Fixed

- Using a timing decorator on an async function should now properly measure the
  execution time, instead of counting immediately. See #119.

Version 3.3
-----------

- Drop support for Python 2.5, 2.6, 3.2, 3.3 (#108, #116).
- Add UnixSocketStatsClient (#76, #112).
- Add support for timedeltas in timing() (#104, #111).
- Fix timer decorator with partial functions (#85).
- Remove ABCMeta metaclass (incompatible with Py3) (#109).
- Refactor client module (#115).
- Various doc updates (#99, #102, #110, #113, #114).


Version 3.2.2
-------------

- Use a monotomic timer to avoid clock adjustments (#96).
- Test on Python 3.5 and 3.6.
- Various doc updates.


Version 3.2.1
-------------

- Restore `StatsClient(host, port, prefix)` argument order.


Version 3.2
-----------

- Add an explicit IPv6 flag.
- Add support for sub-millisecond timings


Version 3.1
-----------

- Add IPv6 support.
- Add TCPStatsClient/TCPPipeline to support connection-mode clients.


Version 3.0.1
-------------

- Make timers-as-decorators threadsafe.


Version 3.0
-----------

- Moved default client instances out of __init__.py. Now find them in
  the `statsd.defaults.{django,env}` modules.


Version 2.1.2
-------------

- Fix negative absolute (non-delta) gauges.
- Improve test coverage.


Version 2.1.1
-------------

- Fix issue with timers used as decorators.


Version 2.1
-----------

- Add maxudpsize option for Pipelines.
- Add methods to use Timer objects directly.

Version 2.0.3
-------------

- Handle large numbers in gauges correctly.
- Add `set` type.
- Pipelines use parent client's _after method.


Version 2.0.2
-------------

- Don't try to pop stats off an empty pipeline.
- Fix installs with Django 1.5 on the PYTHONPATH.


Version 2.0.1
-------------

- Fix install with Django 1.5 in the environment.


Version 2.0
-----------

- Add Pipeline subclass for batching.
- Added an _after method subclasses can use to change behavior.
- Add support for gauge deltas.


Version 1.0
-----------

- Clean up tests and requirements.
- Encode socket data in ASCII.
- Tag v1.


Version 0.5.1
-------------

- Stop supporting IPv6. StatsD doesn't support it, and it breaks things.
- incr, decr, and gauge now support floating point values.


Version 0.5.0
-------------

- Add support for gauges.
- Add real docs and hook up ReadTheDocs.
- Add support for environment var configuration.


Version 0.4.0
-------------

- Look up IP addresses once per client instance.
- Support IPv6.


Version 0.3.0
-------------

- Improve StatsClient.timer.
- Remove nasty threadlocal stuff.
- Return result of StatsClient.timer.


Version 0.2.0
-------------

- Optional prefix for all stats.
- Introduce StatsClient.timer context decorator.
