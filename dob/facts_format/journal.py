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

from click_hotoffthehamster._compat import term_len

from dob_bright.termio import attr, click_echo

__all__ = (
    'output_time_journal',
)


def _generate_table_color_headers(plain_headers):
    # Colorful headers.
    color_headers = []
    for header in plain_headers:
        color_headers.append(
            '{}{}{}'.format(attr('underlined'), header, attr('reset'),),
        )
    return color_headers


def output_time_journal(
    table,
):
    """"""

    def _output_time_journal():
        section_row = None
        for table_row in table:
            section_row = check_section(table_row, section_row)
            output_row(table_row, section_row)

    def check_section(table_row, section_row):
        if section_row is None or table_row[0] != section_row[0]:
            return start_section(table_row)
        return section_row

    def start_section(table_row):
        # Emit a blank line
        click_echo('')
        return table_row

    def output_row(table_row, section_row):
        line = ''

        if table_row is section_row:
            line += table_row[0]
        else:
            # Strip Unicode/ASNI control characters to compute whitespace to fill.
            line += ' ' * term_len(table_row[0])

        i_remainder = 1

        # Omit final column, start_date_cmp, used to sort table in post.
        line += '  ' + '  '.join([str(val) for val in table_row[i_remainder:-1]])

        click_echo(line)

    _output_time_journal()

