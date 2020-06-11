# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob

"""
Packaging instruction for setup tools.

Refs:

  https://setuptools.readthedocs.io/

  https://packaging.python.org/en/latest/distributing.html

  https://github.com/pypa/sampleproject
"""

from setuptools import find_packages, setup

# *** Package requirements.

requirements = [
    # "textwrap, but savvy to ANSI colors"
    #  https://github.com/jonathaneunice/ansiwrap
    'ansiwrap >= 0.8.4, < 1',
    # Vocabulary word pluralizer.
    #  https://github.com/ixmatus/inflector
    'Inflector >= 3.0.1, < 4',
    # https://github.com/mnmelo/lazy_import
    'lazy_import >= 0.2.2, < 1',
    # Tabulate is one of the many table formatter choices.
    #  https://bitbucket.org/astanin/python-tabulate
    'tabulate >= 0.8.7, < 1',
    # Texttable is one of the many table formatter choices.
    #  https://github.com/bufordtaylor/python-texttable
    'texttable >= 1.6.2, < 2',

    # *** HOTH packages.

    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    #    'click',
    #  - Still, had to make one adjustment, and too impatient to ask for a pull...
    #  https://github.com/hotoffthehamster/click
    'click-hotoffthehamster == 7.1.1',
    # Indispensable aliases support for Click.
    #  Upstream at: https://github.com/click-contrib/click-aliases
    #  Released at: https://github.com/hotoffthehamster/click-hotoffthehamster-alias
    'click-hotoffthehamster-alias == 1.0.2',
    # Elapsed timedelta formatter, e.g., "1.25 days".
    # - Imports as `pedantic_timedelta`.
    #  https://github.com/hotoffthehamster/human-friendly_pedantic-timedelta
    'human-friendly_pedantic-timedelta == 2.0.0',
    # The heart of Hamster. (Ye olde `hamster-lib`).
    #  https://github.com/hotoffthehamster/nark
    'nark == 3.2.1',
    # The controller, config, and common output and error tossing code.
    #  https://github.com/hotoffthehamster/dob-bright
    'dob-bright == 1.2.1',
    # The so-called Facts "carousel" chrono-viewer.
    #  https://github.com/hotoffthehamster/dob-viewer
    'dob-viewer == 1.2.1',
]

# *** Minimal setup() function -- Prefer using config where possible.

# (lb): Most settings are in setup.cfg, except identifying packages.
# (We could find-packages from within setup.cfg, but it's convoluted.)

setup(
    # Run-time dependencies installed on `pip install`. To learn more
    # about "install_requires" vs pip's requirements files, see:
    #   https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # Specify which package(s) to install.
    # - Without any rules, find_packages returns, e.g.,
    #     ['dob', 'tests', 'tests.dob']
    # - With the 'exclude*' rule, this call is essentially:
    #     packages=['dob']
    packages=find_packages(exclude=['tests*']),

    # Tell setuptools to determine the version
    # from the latest SCM (git) version tag.
    #
    # Note that if the latest commit is not tagged with a version,
    # or if your working tree or index is dirty, then the version
    # from git will be appended with the commit hash that has the
    # version tag, as well as some sort of 'distance' identifier.
    # E.g., if a project has a '3.0.0a21' version tag but it's not
    # on HEAD, or if the tree or index is dirty, the version might
    # be:
    #   $ python setup.py --version
    #   3.0.0a22.dev3+g6f93d8c.d20190221
    # But if you clean up your working directory and move the tag
    # to the latest commit, you'll get the plain version, e.g.,
    #   $ python setup.py --version
    #   3.0.0a31
    # Ref:
    #   https://github.com/pypa/setuptools_scm
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

