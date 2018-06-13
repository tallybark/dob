#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Packaging instruction for setup tools.

  https://setuptools.readthedocs.io/
"""

import os
import re
from gettext import gettext as _  # Because exec(init_py): noqa: EXXX

try:
    # from setuptools import setup, find_packages
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requirements = [
    # Platform-specific directory magic.
    #  https://github.com/ActiveState/appdirs
    'appdirs',
    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    'Click',
    # Indispensable aliases support for Click.
    #  Stolen from: https://github.com/click-contrib/click-aliases
    #  Released at: https://github.com/hotoffthehamster/click-alias
    'click-alias >= 0.1.0a1',
    # Enable Click color support (we don't use colorama directly).
    #  http://click.pocoo.org/5/utils/#ansi-colors
    'colorama',
    # Python 2 configparser backport.
    #  https://docs.python.org/3/library/configparser.html
    'configparser >= 3.5.0b2',
    # Compatibility layer between Python 2 and Python 3.
    #  https://python-future.org/
    'future',
    # Vocabulary word pluralizer.
    'Inflector',
    # The heart of Hamster. (Ye olde `hamster-lib`).
    'nark',
    # Humanfriendly is one of the many table formatter choices.
    #  https://github.com/xolox/python-humanfriendly
    'humanfriendly',
    # Human Friendly timedelta formatter, e.g., "1 day, 4 hours, 4 mins."
    'human-timedelta',
    # Pyfiglet FIGlet port, for making large letters out of ordinary text.
    #  https://github.com/pwaller/pyfiglet
    # Good work, Frank, Ian, and Glenn! Great LETters!
    'pyfiglet',
    # Just Another EDITOR package.
    #  https://github.com/fmoo/python-editor
    'python-editor',
    # Virtuous Six Python 2 and 3 compatibility library.
    #  https://six.readthedocs.io/
    'six',
    # Tabulate is one of the many table formatter choices.
    #  https://bitbucket.org/astanin/python-tabulate
    'tabulate',
    # Texttable is one of the many table formatter choices.
    #  https://github.com/bufordtaylor/python-texttable
    'texttable',
]


# *** Boilerplate setuptools helper fcns.

# Source values from the top-level {package}/__init__.py,
# to avoid hardcoding herein.

# (lb): I was inspired by PPT's get_version() to write this mess.
# Thank you, PPT!

def top_level_package_file_path(package_dir):
    """Return path of {package}/__init__.py file, relative to this module."""
    path = os.path.join(
        os.path.dirname(__file__),
        package_dir,
        '__init__.py',
    )
    return path


def top_level_package_file_read(path):
    """Read the file at path, and decode as UTF-8."""
    with open(path, 'rb') as f:
        init_py = f.read().decode('utf-8')
    return init_py


def looks_like_app_code(line):
    """Return True if the line looks like `key = ...`."""
    matches = re.search("^\S+ = \S+", line)
    return matches is not None


def top_level_package_file_strip_imports(init_py):
    """Stip passed array of leading entries not identified as `key = ...` code."""
    # Expects comments, docstrings, and imports up top; ``key = val`` lines below.
    culled = []
    past_imports = False
    for line in init_py.splitlines():
        if not past_imports:
            past_imports = looks_like_app_code(line)
        if past_imports:
            culled.append(line)
    return "\n".join(culled)


def import_business_vars(package_dir):
    """Source the top-level __init__.py file, minus its import statements."""
    pckpath = top_level_package_file_path(package_dir)
    init_py = top_level_package_file_read(pckpath)
    source = top_level_package_file_strip_imports(init_py)
    exec(source)
    cfg = { key: val for (key, val) in locals().items() if key.startswith('__') }
    return cfg

# Import variables from nark/__init__.py,
# without triggering that files' imports.
cfg = import_business_vars('nark')

# *** Local file content.

long_description = open(
    os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    )
).read()

# *** Package definition.

setup(
    name=cfg['__pipname__'],
    version=cfg['__version__'],
    author=cfg['__author__'],
    author_email=cfg['__author_email__'],
    url=cfg['__projurl__'],
    description=cfg['__briefly__'],
    long_description=long_description,
    # packages=find_packages(),
    packages=['dob', ],
    package_dir={'dob': 'dob'},
    install_requires=requirements,
    license="GPL3",
    zip_safe=False,
    keywords=cfg['__keywords__'],
    classifiers=[
        # FIXME/2018-06-13: Our goal (this Summer?): Production/Stable.
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        # 'Topic :: Artistic Software',
        'Topic :: Office/Business :: News/Diary',
        # 'Topic :: Religion',  # Because Hamster *is* is religion!
        'Topic :: Text Processing',
    ],
    # <app>=<pkg>.<cls>.run
    entry_points='''
    [console_scripts]
    dob=dob.dob:run
    '''.strip()
)

