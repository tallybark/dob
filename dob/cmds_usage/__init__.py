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

"""``dob usage`` commands."""

from gettext import gettext as _

from pedantic_timedelta import PedanticTimedelta

from dob_bright.reports.render_results import render_results

__all__ = ('generate_usage_table', )


def generate_usage_table(
    controller,
    results,
    name_header=None,
    name_fmttr=lambda item: item.name if item else '<NULL>',
    hide_usage=False,
    hide_duration=False,
    output_format='table',
    table_style='texttable',
    output_path=None,
    chop=False,
):
    def generate_usage_table():
        staged = []
        max_width_tm_value = 0
        max_width_tm_units = 0
        for item, count, duration in results:
            (
                tm_fmttd, tm_scale, tm_units,
            ) = PedanticTimedelta(days=duration or 0).time_format_scaled()
            value, units = tm_fmttd.split(' ')
            max_width_tm_value = max(max_width_tm_value, len(value))
            max_width_tm_units = max(max_width_tm_units, len(units))
            staged.append((item, count, tm_fmttd))

        rows = []
        for item, count, tm_fmttd in staged:
            value, units = tm_fmttd.split(' ')
            span = '{0:>{1}} {2:^{3}}'.format(
                value, max_width_tm_value, units, max_width_tm_units,
            )

            rows.append((name_fmttr(item), count, span))

        culled = cull_results(rows)

        headers = prepare_headers()

        render_results(
            controller,
            results=culled,
            headers=headers,
            output_format=output_format,
            table_style=table_style,
            output_path=output_path,
            chop=chop,
        )

    def cull_results(results):
        if not hide_usage and not hide_duration:
            return results

        resulted = []
        for result in results:
            newr = [result[0]]
            if not hide_usage:
                newr.append(result[1])
            if not hide_duration:
                newr.append(result[2])
            resulted.append(newr)
        return resulted

    def prepare_headers():
        first_header = name_header
        if first_header is None:
            first_header = _("Name")
        headers = [first_header]
        if not hide_usage:
            headers.append(_("Uses"))
        if not hide_duration:
            headers.append(_("Total Time"))
        return headers

    generate_usage_table()

