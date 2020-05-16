# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma, © 2015-2016 Eric Goller.  All rights reserved.
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

import click_hotoffthehamster as click

__all__ = (
    'cmd_options_edit_item',
    'cmd_options_fact_add',
    'cmd_options_fact_dryable',
    'cmd_options_fact_edit',
    'cmd_options_fact_import',
    'cmd_options_factoid',
    'cmd_options_factoid_verify_none',
    'cmd_options_factoid_verify_start',
    'cmd_options_factoid_verify_end',
    'cmd_options_factoid_verify_both',
    'cmd_options_rule_name',
    'cmd_options_styles_internal',
    'cmd_options_styles_named',
)


# ***
# *** [ADD FACT/STOP FACT] Raw Factoid Option.
# ***

_option_factoid_text_parts = (
    '[<activity>[@<category>]]'
    ' [@<tag>...] [<description>]'
)


_cmd_options_factoid = [
    click.argument('factoid', nargs=-1, default=None,
                   metavar='[START_TIME] [to] [END_TIME] {}'.format(
                       _option_factoid_text_parts,
                   )),
]


def cmd_options_factoid(func):
    for option in reversed(_cmd_options_factoid):
        func = option(func)
    return func


_cmd_options_factoid_verify_none = [
    click.argument('factoid', nargs=-1, default=None,
                   metavar=_option_factoid_text_parts,
                   ),
]


def cmd_options_factoid_verify_none(func):
    for option in reversed(_cmd_options_factoid_verify_none):
        func = option(func)
    return func


_cmd_options_factoid_verify_start = [
    click.argument('factoid', nargs=-1, default=None,
                   metavar='[START_TIME] {}'.format(
                       _option_factoid_text_parts,
                   )),
]


def cmd_options_factoid_verify_start(func):
    for option in reversed(_cmd_options_factoid_verify_start):
        func = option(func)
    return func


_cmd_options_factoid_verify_end = [
    click.argument('factoid', nargs=-1, default=None,
                   metavar='[END_TIME] {}'.format(
                       _option_factoid_text_parts,
                   )),
]


def cmd_options_factoid_verify_end(func):
    for option in reversed(_cmd_options_factoid_verify_end):
        func = option(func)
    return func


_cmd_options_factoid_verify_both = [
    click.argument('factoid', nargs=-1, default=None,
                   metavar='START_TIME to END_TIME {}'.format(
                       _option_factoid_text_parts,
                   )),
]


def cmd_options_factoid_verify_both(func):
    for option in reversed(_cmd_options_factoid_verify_both):
        func = option(func)
    return func


# ***
# *** [ADD FACT] Options.
# ***

_cmd_options_fact_add_prefix = [
    click.option(
        '-e', '--editor', is_flag=True,
        help=_('Edit new Fact before saving, using Carousel, and Awesome Prompt.'),
    ),
]


_cmd_options_fact_add_and_edit = [
    click.option(
        '-d', '--edit-text', is_flag=True,
        help=_('Edit description using user’s preferred $EDITOR.'),
    ),
    click.option(
        '-a', '--edit-meta', is_flag=True,
        help=_('Ask for act@gory and tags using Awesome Prompt.'),
    ),
]


_cmd_options_fact_add_postfix = [
    # (lb): 2019-02-01: Current thinking is that conflicts are only okay
    # on add-fact, and only outside the context of the Carousel. So applies
    # to dob-add commands, but not to dob-import.
    click.option(
        '-y', '--yes', is_flag=True,
        help=_('Save conflicts automatically, otherwise ask for confirmation.'),
    ),
]


def cmd_options_fact_add(func):
    for option in reversed(
        _cmd_options_fact_add_prefix
        + _cmd_options_fact_add_and_edit
        + _cmd_options_fact_add_postfix
    ):
        func = option(func)
    return func


# ***
# *** [IMPORT FACTS] Options.
# ***

_cmd_options_fact_import = [
    # (lb): This is similar to dob-add's --edit, except the default is reversed.
    # - On dob-add, default is to not run Carousel; but on dob-import, it is.
    click.option(
        # Option skips carousel, opens Content in EDITOR, saves Fact on EDITOR exit.
        '-E', '--no-editor', is_flag=True,
        help=_('Skip interactive editor after import. Save Facts and exit.'),
    ),
]


def cmd_options_fact_import(func):
    for option in reversed(_cmd_options_fact_import):
        func = option(func)
    return func


# ***
# *** [EDIT FACT] Options.
# ***

_cmd_options_fact_no_editor_edit = [
    click.option(
        '-E', '--no-editor', is_flag=True,
        help=_('Skip interactive editor. Use $EDITOR and Awesome Prompt.'),
    ),
]


def cmd_options_fact_edit(func):
    for option in reversed(
        _cmd_options_fact_add_and_edit
        + _cmd_options_fact_no_editor_edit
    ):
        func = option(func)
    return func


# ***
# *** [ADD FACT/IMPORT FACT(S)] Shared Options.
# ***

_cmd_options_fact_dryable = [
    # (lb): The --dry option is not super useful if you have your store under
    # git control, because you can easily revert any changes; or if you setup a
    # test store under /tmp (i.e., `export XDG_DATA_HOME=/tmp/xxx/.local/share`).
    # It's really just more code to test!
    # MAYBE/2019-02-01: Remove the --dry option, and save a unittest?
    click.option(
        '--dry', is_flag=True,
        help=_('Dry run: do not make changes.'),
    ),
]


def cmd_options_fact_dryable(func):
    for option in reversed(_cmd_options_fact_dryable):
        func = option(func)
    return func


# ***
# *** [EDIT ITEM] Options.
# ***

_cmd_options_edit_item = [
    # User can indicate specific item to edit via its PK, otherwise default to latest.
    # FIXME/BACKLOG/2019-01-31: Could allow user to specify datetime instead of PK,
    #   e.g., `dob edit 2019-01-31` could bring up Fact at Noon on specific day (or
    #   midnight).
    click.argument('key', nargs=1, type=int, required=False),
    # (lb): User can specify specific Fact PK, a positive integer, or user
    # can specify an index relative to the last Fact, e.g., `dob edit -1`
    # (or even `dob edit -2`, though anything other than `dob edit -1` seems
    # useless, i.e., would a user ever really run `dob edit -5`?). In any case,
    # because the negative relative index starts with the dash '-' character,
    # Click will complain if it parses the argument as an option, e.g.,
    #   $ dob edit -1
    #   Error: no such option: -1
    # The user can double-dash to tell Click to stop option processing, e.g.,
    #   $ dob edit -- -1
    # The latter is somewhat clunky, so we can make '-1' an option.
    # Note that this doesn't solve the issue for -2, -3, etc., but really, who cares.
    click.option(
        '-1', 'latest_1', is_flag=True,
        help=_('Edit most recent Fact (latest complete, or active).'),
    ),
]


def cmd_options_edit_item(func):
    for option in reversed(_cmd_options_edit_item):
        func = option(func)
    return func


# ***
# *** [STYLES] Options.
# ***

_cmd_options_styles_internal = [
    click.option(
        '-i', '--internal', is_flag=True,
        help=_(
            'Print pristine or internal style settings, not raw styles.conf section. '
            'If the named style is also a section in styles.conf, '
            'this exclude comments, and it reorders the settings. '
            'Otherwise, if not in styles.conf, the matching internal style is located.'
        )
    ),
]


def cmd_options_styles_internal(func):
    for option in reversed(_cmd_options_styles_internal):
        func = option(func)
    return func


_cmd_options_styles_named = [
    click.argument('name', nargs=1, default='', metavar=_('[STYLE_NAME]')),
]


def cmd_options_styles_named(func):
    for option in reversed(_cmd_options_styles_named):
        func = option(func)
    return func


# ***
# *** [RULES] Options.
# ***

_cmd_options_rule_name = [
    click.argument('name', nargs=1, default='', metavar=_('[RULE_NAME]')),
]


def cmd_options_rule_name(func):
    for option in reversed(_cmd_options_rule_name):
        func = option(func)
    return func

