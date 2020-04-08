# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma.  All rights reserved.
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

from gettext import gettext as _

import ansiwrap
import click_hotoffthehamster as click
from click_hotoffthehamster.formatting import wrap_text
from click_hotoffthehamster._textwrap import TextWrapper

from dob_bright.termio import attr, click_echo, dob_in_user_exit, fg

from ..clickux.help_strings import NO_ACTIVE_FACT_HELP

__all__ = (
    'echo_fact',
    'echo_latest_ended',
    'echo_ongoing_fact',
    'echo_ongoing_or_ended',
    # Private:
    #  'echo_most_recent',
    #  'echo_single_fact',
)


# ***

def echo_fact(fact):
    click.echo('{}Dry run! New fact{}:\n '.format(
        attr('underlined'),
        attr('reset'),
    ))
    click.echo('{}{}{}{}'.format(
        fg('steel_blue_1b'),
        attr('bold'),
        fact.friendly_str(description_sep='\n\n'),
        attr('reset'),
    ))


# ***

def echo_latest_ended(controller):
    echo_most_recent(controller, restrict='ended')


def echo_ongoing_fact(controller):
    """
    Return current active Fact.

    Returns:
        None: If everything went alright.

    Raises:
        click.ClickException: If we fail to fetch any active Fact.
    """
    echo_most_recent(
        controller,
        restrict='ongoing',
        empty_msg=NO_ACTIVE_FACT_HELP(controller.ctx),
    )


def echo_ongoing_or_ended(controller):
    echo_most_recent(controller, restrict=None)


def echo_most_recent(controller, restrict=None, empty_msg=None):
    fact = controller.find_latest_fact(restrict=restrict)
    if fact is not None:
        echo_single_fact(controller, fact)
    else:
        empty_msg = empty_msg if empty_msg else _('No facts found.')
        dob_in_user_exit(empty_msg)


# ***

class AnsiWrapper(TextWrapper):

    def __init__(self, *args, **kwargs):
        super(AnsiWrapper, self).__init__(*args, **kwargs)

    def fill(self, *args, **kwargs):
        return ansiwrap.fill(*args, width=self.width, **kwargs)


def echo_single_fact(controller, fact):
    colorful = controller.config['term.use_color']
    localize = controller.config['time.tz_aware']
    friendly = fact.friendly_str(
        shellify=False,
        description_sep=': ',
        localize=localize,
        colorful=colorful,
        show_elapsed=True,
    )
    # Click's default wrap_text behavior uses Click TextWrapper class, which
    # extends Python's textwrap.TextWrapper, which is not ANSI-aware. So we
    # extent TextWrapper to redirect it to ansiwrap, which is ANSI-couth.
    # FIXME/2019-11-22: (lb): Make this width CONFIGable.
    wrapped = wrap_text(friendly, width=100, preserve_paragraphs=True, cls=AnsiWrapper)
    click_echo(wrapped)


# ***

def write_fact_block_format(fact_f, fact, rule, is_first_fact):
    write_fact_separator(fact_f, rule, is_first_fact)
    friendly_str = fact.friendly_str(
        # description_sep='\n\n',
        description_sep=': ',
        shellify=False,
        colorful=False,
        omit_empty_actegory=True,
    )
    fact_f.write(friendly_str)


def write_fact_separator(fact_f, rule, is_first_fact):
    RULE_WIDTH = 76  # How wide to print the between-facts separator.
    if is_first_fact:
        return
    fact_f.write('\n\n')
    if rule:
        fact_f.write('{}\n\n'.format(rule * RULE_WIDTH))

