from setuptools import setup, find_packages

setup(
    name='statsd',
    version='1.0.0',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
