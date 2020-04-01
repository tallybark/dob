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

from nark import get_version as _get_version

__all__ = (
    'get_version',
    '__arg0name__',
    '__author_name__',
    '__author_link__',
    '__package_name__',
)

__arg0name__ = os.path.basename(sys.argv[0])

# (lb): These are duplicated in setup.cfg:[metadata], but not sure how to DRY.
#   Fortunately, they're not likely to change.
__author_name__ = 'Landon Bouma'
__author_link__ = 'https://tallybark.com'

# (lb): Not sure if the package name is available at runtime. Seems kinda meta,
# anyway, like, Who am I? I just want to avoid hard coding this string in docs.
# (And it's also used for making the `dob version` output.)
__package_name__ = 'dob'


def get_version(include_head=False):
    return _get_version(
        package_name=__package_name__,
        reference_file=__file__,
        include_head=include_head,
    )

