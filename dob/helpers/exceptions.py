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
""""""

from __future__ import absolute_import, unicode_literals

from functools import update_wrapper

__all__ = [
    'catch_action_exception',
]


def catch_action_exception(func):
    def wrapper(self, event=None, *args, **kwargs):
        try:
            return func(self, event=event, *args, **kwargs)
        except Exception as err:
            import traceback
            traceback.print_stack()
            traceback.print_exc()
            import pdb
            pdb.set_trace()
            raise

    return update_wrapper(wrapper, func)

