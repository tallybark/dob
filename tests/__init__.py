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

"""Testsuite for ``dob``."""

from __future__ import absolute_import, unicode_literals

import datetime

__all__ = [
    'truncate_to_whole_seconds',
]


def truncate_to_whole_seconds(time):
    time_fmt = '%Y-%m-%d %H:%M'
    return datetime.datetime.strptime(time.strftime(time_fmt), time_fmt)

