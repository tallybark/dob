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

from functools import update_wrapper

__all__ = (
    'catch_action_exception',
)


def catch_action_exception(func):
    def wrapper(self, event=None, *args, **kwargs):
        try:
            return func(self, event=event, *args, **kwargs)
        except Exception as err:  # noqa: F841
            # F841 local variable '...' is assigned to but never used

            if not self.carousel.controller.config['dev.catch_errors']:
                # MAYBE/2019-01-21: Display warning and silently recover.
                #  But really, harden the code, and do not expect this path.
                raise

            import traceback
            traceback.print_stack()
            traceback.print_exc()
            # We're gonna die anyway, so undo terminal raw mode, if PPT did so.
            import os
            os.system('stty sane')
            import pdb
            pdb.set_trace()
            raise

    return update_wrapper(wrapper, func)

