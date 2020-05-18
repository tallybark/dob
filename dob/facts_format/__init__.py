# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

"""Top-level package module for output format modules."""

from gettext import gettext as _

from dob_bright.termio import dob_in_user_warning

__all__ = (
    'echo_warn_if_truncated',
)


def echo_warn_if_truncated(controller, n_results, n_rows):
    if n_results <= n_rows:
        return

    dob_in_user_warning(_(
        'Showed only {} of {} results. Use `-C term.row_limit=0` to see all results.'
    ).format(format(n_results, ','), format(n_rows, ',')))

