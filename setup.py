from importlib.machinery import SourceFileLoader
from pathlib import Path
from setuptools import setup

THIS_DIR = Path(__file__).resolve().parent
long_description = THIS_DIR.joinpath('README.rst').read_text()

# avoid loading the package before requirements are installed:
version = SourceFileLoader('version', 'aiohttp_prodtools/version.py').load_module()

setup(
    name='aiohttp-prodtools',
    version=str(version.VERSION),
    description='Tools for aiohttp in production',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Environment :: MacOS X',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    author='Samuel Colvin',
    author_email='s@muelcolvin.com',
    url='https://github.com/aio-libs/aiohttp-prodtools',
    license='MIT',
    packages=['aiohttp_prodtools'],
    zip_safe=True,
    # entry_points="""
    #     [console_scripts]
    #     aprod=aiohttp_prodtools.cli:cli
    #     aiohttp-prodtools=aiohttp_prodtools.cli:cli
    # """,
    install_requires=['aiohttp>=2.0.0'],
)
