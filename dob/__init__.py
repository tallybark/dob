# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
#
# 'dob' is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License  as  published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any   later    version.
#
# 'dob' is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY  or  FITNESS FOR A PARTICULAR
# PURPOSE.  See  the  GNU General Public License  for  more details.
#
# You can find the GNU General Public License reprinted in the file titled 'LICENSE',
# or visit <http://www.gnu.org/licenses/>.

"""``hamster``, ``hamster``, ``hamster``!!! a cuddly, furry time tracker."""

import os
import sys

__all__ = (
    '__arg0name__',
    '__author_name__',
    '__author_link__',
    '__package_name__',
    '__resolve_vers__',
)

# (lb): These are duplicated in setup.cfg:[metadata], but not sure how to DRY.
#   Fortunately, they're not likely to change.
__author_name__ = 'Landon Bouma'
__author_link__ = 'https://tallybark.com'

# (lb): Not sure if the package name is available at runtime. Seems kinda meta,
# anyway, like, Who am I? I just want to avoid hard coding this string in docs.
__package_name__ = 'dob'
__arg0name__ = os.path.basename(sys.argv[0])


def __resolve_vers__():
    """Returns the installed package version, or '<none>'.

    In lieu of always setting __version__ -- and always loading pkg_resources --
    use a method to avoid incurring startup costs if the version is not needed.
    """
    try:
        import setuptools_scm
        # For whatever reason, relative_to does not work, (lb) thought it would.
        #   return setuptools_scm.get_version(relative_to=__file__)
        pkg_dirname = os.path.dirname(os.path.dirname(__file__))
        # See if parent directory (of this file) contains .git/.
        proj_git = os.path.join(pkg_dirname, '.git')
        if os.path.exists(proj_git):
            # Get version from setuptools_scm, and git tags.
            # This is similar to a developer running, e.g.,
            #   python setup.py --version
            return setuptools_scm.get_version(root=pkg_dirname)
    except ImportError:
        # ModuleNotFoundError added py3.6. Until then, ImportError.
        from pkg_resources import get_distribution, DistributionNotFound
        try:
            return get_distribution(__package_name__).version
        except DistributionNotFound:
            return '<none>'
    else:
        return '<none>'

