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

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from ..helpers import dob_in_user_exit

__all__ = (
    'must_no_more_than_one_file',
)


def must_no_more_than_one_file(filename):
    # Because nargs=-1, the user could specify many files! E.g.,
    #
    #   dob import file1 file2
    #
    # Also, click supports the magic STDIN identifier, `-`, e.g.,
    #
    #   dob import -
    #
    # will read from STDIN.
    #
    # (And `dob import - <file>` will open 2 streams!)
    if len(filename) > 1:
        msg = _('Please specify only one input, file or STDIN!')
        dob_in_user_exit(msg)
    elif filename:
        return filename[0]
    else:
        return None

