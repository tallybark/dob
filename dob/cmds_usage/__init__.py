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

"""``dob usage`` commands."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from pedantic_timedelta import PedanticTimedelta

from ..helpers.ascii_table import generate_table

__all__ = ['generate_usage_table']


def generate_usage_table(
    results,
    name_fmttr=lambda item: item.name,
    table_type='friendly',
    truncate=False,
):
    headers = (_("Name"), _("Uses"), _("Total Time"))

    staged = []
    max_width_tm_value = 0
    max_width_tm_units = 0
    for activity, count, duration in results:
        (
            tm_fmttd, tm_scale, tm_units,
        ) = PedanticTimedelta(days=duration).time_format_scaled()
        value, units = tm_fmttd.split(' ')
        max_width_tm_value = max(max_width_tm_value, len(value))
        max_width_tm_units = max(max_width_tm_units, len(units))
        staged.append((activity, count, tm_fmttd))

    rows = []
    for item, count, tm_fmttd in staged:
        value, units = tm_fmttd.split(' ')
        span = '{0:>{1}} {2:^{3}}'.format(
            value, max_width_tm_value, units, max_width_tm_units,
        )

        rows.append((name_fmttr(item), count, span))

    generate_table(rows, headers, table_type, truncate, trunccol=0)

