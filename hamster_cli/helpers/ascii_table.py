# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
from colored import fg, bg, attr

# (lb): I know, I know, 3 table libraries! I couldn't find one I liked the
# best, so now they're all included, and the user can choose their fave.
from tabulate import tabulate
from texttable import Texttable
from humanfriendly.tables import format_pretty_table


def generate_table(
    rows,
    headers,
    table_type='friendly',
    truncate=False,
    trunccol=None
):
    """Generates an ASCII table using the generator specified by table_type."""
    # Add some flair to the header labels.
    plain_headers = headers
    color_headers = _generate_table_color_headers(plain_headers)
    # Determine the max_width of the elastic cell; or use 0, if not truncating.
    max_width = _generate_table_max_width(rows, table_type, truncate, trunccol)
    # Truncate long values in the trunccol column, if requested.
    trows = _generate_table_truncate_cell_values(rows, trunccol, max_width)
    _generate_table_display(trows, plain_headers, color_headers, table_type)

def _generate_table_color_headers(plain_headers):
    # Colorize headers.
    color_headers = []
    for header in plain_headers:
        color_headers.append(
            '{}{}{}'.format(attr('underlined'), header, attr('reset'),),
        )
    return color_headers

def _generate_table_max_width(rows, table_type, truncate, trunccol):
    if not truncate or not rows:
        return 0
    num_cols = len(rows[0])
    assert trunccol is not None
    column_width_used = _generate_table_width_content(rows, num_cols, trunccol)
    border_width_used = _generate_table_width_border(rows, num_cols, table_type)

    # Determine the width available for the elastic column.
    term_width, _term_height = click.get_terminal_size()
    ellipsis_width = len('...')
    max_width = term_width - (border_width_used + column_width_used + ellipsis_width)
    max_width = max(0, max_width)
    return max_width

def _generate_table_width_content(rows, num_cols, trunccol):
    # Calculate max column widths.
    max_widths = [0] * num_cols
    for row in rows:
        for idx, col in enumerate(row):
            max_widths[idx] = max(max_widths[idx], len(str(col)))
    column_width_used = 0
    for idx, width in enumerate(max_widths):
        if idx == trunccol:
            continue
        column_width_used += width
    return column_width_used

def _generate_table_width_border(rows, num_cols, table_type):
    n_inner_borders = num_cols - 1
    # FIXME/2018-05-11 22:09: (lb): This looks nice for 2 columns. Not sure on others.
    border_width_used = (
        len('│ ') + (n_inner_borders * len(' │   ')) + len(' │')
    )
    # (lb): Does this computation work for all formatters and table styles?
    #   tabulate: seems to be exact (table abuts right edge)
    #   texttable: 2 off (but only if terminal narrower than default table width)
    #   friendly: also 2 off
    # ... at least for the currently chosen table border designs.
    if table_type in ('texttable', 'friendly'):
        # MAGIC_NUMBER: Nudge these formatters' widths inward a titch.
        border_width_used -= 2
    # MAGIC_NUMBER: (lb): I like a 1 character column gutter.
    border_width_used += 1
    return border_width_used

def _generate_table_truncate_cell_values(rows, trunccol, max_width):
    trows = []
    for row in rows:
        trow = list(row)
        trows.append(trow)
        if (max_width > 0) and (len(trow[trunccol]) >= max_width):
            trow[trunccol] = trow[trunccol][:max_width] + '...'
    return trows

def _generate_table_display(rows, plain_headers, color_headers, table_type):
    if table_type == 'tabulate':
        #click.echo(tabulate(rows, headers=color_headers))
        click.echo(tabulate(rows, headers=color_headers, tablefmt="fancy_grid"))
    elif table_type == 'texttable':
        # PROS: Texttable wraps long lines by **default**!
        #       And within the same column!
        #         So you don't need to --truncate.
        #       It even defaults to a nice, narrow, 80-character wide table.
        #       You can set it wider, e.g., Texttable(max_width=term_width),
        #       but the narrow look is sleek, and easy to read.
        # CONS: Texttable counts control characters.
        #       If you add color to your headers, their columns will not
        #       line up with the content rows! (lb): "A deal breaker!"
        ttable = Texttable()
        ttable.set_cols_align(["l", "r"])
        rows.insert(0, plain_headers)
        ttable.add_rows(rows)
        click.echo(ttable.draw())
    else:
        assert table_type == 'friendly'
        # Haha, humanfriendly colors the header text green by default.
        click.echo(format_pretty_table(rows, color_headers))

