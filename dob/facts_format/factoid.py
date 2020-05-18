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

import sys

import click_hotoffthehamster as click

from dob_bright.termio import click_echo, stylize

from . import echo_warn_if_truncated

__all__ = (
    'output_factoid_list',
)


def output_factoid_list(
    controller,
    results,
    row_limit,
    factoid_rule='',
    out_file=None,
    term_width=None,
    **kwargs
):
    def _output_factoid_list():
        colorful = controller.config['term.use_color']
        sep_width = output_rule_width()
        cut_width = output_truncate_at()
        n_out = 0
        partial_out = False
        for idx, fact in enumerate(results):
            n_out += 1
            if row_limit and row_limit > 0 and n_out > row_limit:
                partial_out = True
                break

            write_out() if idx > 0 else None
            output_fact_block(fact, colorful, cut_width)
            if sep_width:
                write_out()
                write_out(stylize(factoid_rule * sep_width, 'indian_red_1c'))

        if partial_out:
            echo_warn_if_truncated(controller, n_out, len(results))

    def output_rule_width():
        if not factoid_rule:
            return None
        return terminal_width()

    def output_truncate_at():
        if not chop:
            return None
        return terminal_width()

    def terminal_width():
        if term_width is not None:
            return term_width
        elif sys.stdout.isatty():
            return click.get_terminal_size()[0]
        else:
            return 80

    def output_fact_block(fact, colorful, cut_width):
        write_out(
            fact.friendly_str(
                shellify=False,
                description_sep='\n\n',
                localize=True,
                include_id=include_id,
                colorful=colorful,
                cut_width=cut_width,
                show_elapsed=not hide_duration,
            )
        )

    def write_out(line=''):
        if out_file is not None:
            out_file.write(line + "\n")
        else:
            click_echo(line)

    _output_factoid_list()

