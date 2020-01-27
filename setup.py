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
    # "Very simple Python library for color and formatting in terminal."
    # Forked (for italic "support") to:
    #  https://github.com/hotoffthehamster/ansi-escape-room
    # Forked from:
    #  https://gitlab.com/dslackw/colored
    # See wrapper file:
    #  nark/helpers/emphasis.py
    'ansi-escape-room',
    # Nice! Because Click was already halfway there... just not quite.
    # https://github.com/jonathaneunice/ansiwrap
    # (lb): I considered adding this to Click, but Click has no dependencies!
    #       So let's keep it pure.
    'ansiwrap >= 0.8.4',
    # Platform-specific directory magic.
    #  https://github.com/ActiveState/appdirs
    'appdirs',
    # (lb): Click may be the best optparser of any language I've used.
    #  https://github.com/pallets/click
    #    'click',
    #  - Still, had to make one adjustment, and too impatient to ask for a pull...
    #  https://github.com/hotoffthehamster/click
    'click--hotoffthehamster',
    # Indispensable aliases support for Click.
    #  Stolen from: https://github.com/click-contrib/click-aliases
    #  Released at: https://github.com/hotoffthehamster/click-alias
    'click-alias >= 0.1.0a1',
    # Enable Click color support (we don't use colorama directly, but it does),
    #  "on Windows, this ... is only available if colorama is installed".
    #  https://click.palletsprojects.com/en/5.x/utils/#ansi-colors
    #  https://pypi.org/project/colorama/
    'colorama',
    # INI/config parser, even better (preserves comments and ordering).
    #  https://github.com/DiffSK/configobj
    #  https://configobj.readthedocs.io/en/latest/
    'configobj >= 5.0.6',
    # The act@gory and tag prompt interface.
    #  https://github.com/hotoffthehamster/dob-prompt
    'dob-prompt',
    # The so-called Facts "carousel" chrono-viewer.
    #  https://github.com/hotoffthehamster/dob-viewer
    'dob-viewer',
    # Vocabulary word pluralizer.
    #  https://github.com/ixmatus/inflector
    'Inflector',
    # Humanfriendly is one of the many table formatter choices.
    #  https://github.com/xolox/python-humanfriendly
    'humanfriendly',
    # Elapsed timedelta formatter, e.g., "1.25 days".
    # - Imports as `pedantic_timedelta`.
    #  https://github.com/hotoffthehamster/human-friendly_pedantic-timedelta
    'human-friendly_pedantic-timedelta >= 0.0.6',
    # https://github.com/mnmelo/lazy_import
    'lazy_import',
    # The heart of Hamster. (Ye olde `hamster-lib`).
    #  https://github.com/hotoffthehamster/nark
    'nark',
    # Amazeballs prompt library.
    #   https://github.com/prompt-toolkit/python-prompt-toolkit
    #     'prompt-toolkit',
    # - FIXME/2019-02-21: (lb): Need to submit PR, then return to mainline.
    #   https://github.com/hotoffthehamster/python-prompt-toolkit
    'prompt-toolkit-dob >= 2.0.9',  # Imports as prompt_toolkit.
    # Just Another EDITOR package.
    #  https://github.com/fmoo/python-editor
    'python-editor',  # Imports as editor.
    # Tabulate is one of the many table formatter choices.
    #  https://bitbucket.org/astanin/python-tabulate
    'tabulate',
    # Texttable is one of the many table formatter choices.
    #  https://github.com/bufordtaylor/python-texttable
    'texttable',
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

