.. _contributing-chapter:

============
Contributing
============

I happily accept patches if they make sense for the project and work
well. If you aren't sure if I'll merge a patch upstream, please open an
issue_ and describe it.

Patches should meet the following criteria before I'll merge them:

* All existing tests must pass.
* Bugfixes and new features must include new tests or asserts.
* Must not introduce any PEP8 or PyFlakes violations.

I recommend doing all development in a virtualenv_, though this is
really up to you.

It would be great if new or changed features had documentation and
included updates to the ``CHANGES`` file, but it's not totally
necessary.


Running Tests
=============

To run the tests, you just need ``nose`` and ``mock``. These can be
installed with ``pip``::

    $ mkvirtualenv statsd
    $ pip install -r requirements.txt
    $ nosetests

You can also run the tests with tox::

    $ tox

Tox will run the tests in Pythons 2.5, 2.6, 2.7, 3.2, 3.3, 3.4, and
PyPy, if they're available.


Writing Tests
=============

New features or bug fixes should include tests that fail without the
relevant code changes and pass with them.

For example, if there is a bug in the ``StatsClient._send`` method, a
new test should demonstrate the incorrect behavior by failing, and the
associated changes should fix it. The failure can be a FAILURE or an
ERROR.

Tests and the code to fix them should be in the same commit. Bisecting
should not stumble over any otherwise known failures.

.. note::

   Pull requests that only contain tests to demonstrate bugs are
   welcome, but they will be squashed with code changes to fix them.


PEP8 and PyFlakes
=================

The development requirements (``requirements.txt``) include the
``flake8`` tool. It is easy to run::

    $ flake8 statsd/

``flake8`` should not raise any issues or warnings.

.. note::

   The docs directory includes a Sphinx-generated conf.py that has
   several violations. That's fine, don't worry about it.


Documentation
=============

The documentation lives in the ``docs/`` directory and is automatically
built and pushed to ReadTheDocs_.

If you change or add a feature, and want to update the docs, that would
be great. New features may need a new chapter. You can follow the
examples already there, and be sure to add a reference to
``docs/index.rst``. Changes or very small additions may just need a new
heading in an existing chapter.


.. _issue: https://github.com/jsocol/pystatsd/issues
.. _virtualenv: http://www.virtualenv.org/
.. _ReadTheDocs: https://statsd.readthedocs.io/
