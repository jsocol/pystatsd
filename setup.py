from setuptools import setup, find_packages

import statsd

setup(
    name='statsd',
    version=statsd.__version__,
    description='A simple statsd client.',
    long_description=open('README.rst').read(),
    author='James Socol',
    author_email='james@mozilla.com',
    url='https://github.com/jsocol/pystatsd',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['README.rst']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
