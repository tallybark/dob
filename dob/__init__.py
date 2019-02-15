# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

"""``hamster``, ``hamster``, ``hamster``!!! a cuddly, furry time tracker."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import os
import sys

__all__ = [
    '__author__',
    '__author_email__',
    '__version__',
    '__appname__',
    '__pipname__',
    '__briefly__',
    '__projurl__',
    '__keywords__',
    '__BigName__',
    '__libname__',
    '__arg0name__',
]


# SYNC_UP: nark/__init__.py <=> dob/__init__.py
__author__ = 'HotOffThe Hamster'
__author_email__ = 'hotoffthehamster+dob@gmail.com'
__version__ = '3.0.0a27'
__appname__ = 'dob'
__pipname__ = __appname__
__briefly__ = _(
    'journal and time tracker, supercharged for the terminal'
)
__projurl__ = 'https://github.com/hotoffthehamster/dob'
__keywords__ = ' '.join([
    'journal',
    'diary',
    'timesheet',
    'timetrack',
    'jrnl',
    'rednotebook',
    'todo.txt',
    'prjct',
    'hamster',
    'fact',
])
__BigName__ = 'Hamster Dobber'
__libname__ = 'nark'
__arg0name__ = os.path.basename(sys.argv[0])

