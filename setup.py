from setuptools import find_packages, setup


setup(
    name='statsd',
    version='3.3.0',
    description='A simple statsd client.',
    long_description=open('README.rst').read(),
    author='James Socol',
    author_email='james@mozilla.com',
    url='https://github.com/jsocol/pystatsd',
    license='MIT',
    python_requires=">=3.6.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['README.rst']},
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
