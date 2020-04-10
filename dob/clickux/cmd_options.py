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

import inspect

from gettext import gettext as _

import click_hotoffthehamster as click

__all__ = (
    'cmd_options_factoid',
    'cmd_options_fact_add',
    'cmd_options_fact_dryable',
    'cmd_options_fact_edit',
    'cmd_options_fact_import',
    'cmd_options_limit_offset',
    'cmd_options_list_activitied',
    'cmd_options_list_categoried',
    'cmd_options_list_fact',
    'cmd_options_search',
    'cmd_options_table_view',
    'cmd_options_usage',
    'cmd_options_edit_item',
    'postprocess_options_list_activitied',
    'postprocess_options_list_categoried',
    'postprocess_options_table_options',
    'OptionWithDynamicHelp',
    # Private:
    #   '_postprocess_options_table_option_order_to_sort_col',
    #   '_postprocess_options_table_options_asc_desc_to_sort_order',
)


# ***
# *** [TIME RANGE] Options.
# ***

_cmd_options_search = [
    click.option(
        '--since', '--after',
        help=_('Show items more recent than a specific date.'),
    ),
    click.option(
        '--until', '--before',
        help=_('Show items older than a specific date.'),
    ),
    click.option(
        '--deleted', is_flag=True, help=_('Show deleted items.'),
    ),
    click.option(
        '--hidden', is_flag=True, help=_('Show hidden items.'),
    ),
    click.option(
        '-k', '--key', help=_('The database key of the item.'),
    ),
    click.argument('search_term', nargs=-1, default=None),
]


def cmd_options_search(func):
    for option in reversed(_cmd_options_search):
        func = option(func)
    return func


# ***
# *** [LIMIT/OFFSET] Options.
# ***

_cmd_options_limit_offset = [
    click.option(
        '-L', '--limit', default=0, show_default=False,
        help=_('Limit the number of records to fetch.'),
    ),
    click.option(
        '-O', '--offset', default=0, show_default=False,
        help=_('Record offset to fetch.'),
    ),
]


def cmd_options_limit_offset(func):
    for option in reversed(_cmd_options_limit_offset):
        func = option(func)
    return func


# ***
# *** [TABLE BASIC] Options.
# ***

_cmd_options_table_renderer = [
    click.option(
        '-T', '--table-type', default='texttable', show_default=True,
        type=click.Choice(['tabulate', 'texttable', 'friendly']),
        help=_('ASCII table formatter.'),
    ),
]


def cmd_options_table_renderer(func):
    for option in reversed(_cmd_options_table_renderer):
        func = option(func)
    return func


# ***
# *** [TABLE FANCY] Options.
# ***

_cmd_options_table_truncols = [
    click.option(
        '-t', '--truncate', is_flag=True,
        help=_('Truncate long activity@category names.'),
    ),
]


def cmd_options_table_truncols(func):
    for option in reversed(_cmd_options_table_truncols):
        func = option(func)
    return func


_cmd_options_table_order = [
    click.option(
        '-A', '--asc', is_flag=True, default=None,
        help=_('Sort by ascending column value.'),
    ),
    click.option(
        '-D', '--desc', is_flag=True, default=None,
        help=_('Sort by descending column value.'),
    ),
    click.option(
        '-o', '--order', '--sort', default='',
        type=click.Choice([
            '', 'name', 'activity', 'category', 'tag', 'fact', 'start', 'usage', 'time',
        ]),
        help=_('Order by column (may depend on query).'),
    ),
]


def cmd_options_table_order(func):
    for option in reversed(_cmd_options_table_order):
        func = option(func)
    return func


# *** Combining last 3 table-related options into one convenient wrapper.

def cmd_options_table_view(func):
    for option in reversed(
        _cmd_options_table_truncols
        + _cmd_options_table_renderer
        + _cmd_options_table_order
    ):
        func = option(func)
    return func


def postprocess_options_table_options(kwargs):
    _postprocess_options_table_option_order_to_sort_col(kwargs)
    _postprocess_options_table_options_asc_desc_to_sort_order(kwargs)


def _postprocess_options_table_option_order_to_sort_col(kwargs):
    kwargs['sort_col'] = kwargs['order']
    del kwargs['order']
    if not kwargs['sort_col']:
        del kwargs['sort_col']


def _postprocess_options_table_options_asc_desc_to_sort_order(kwargs):
    if kwargs['desc']:
        sort_order = 'desc'
    elif kwargs['asc']:
        sort_order = 'asc'
    else:
        sort_order = ''
    del kwargs['desc']
    del kwargs['asc']
    kwargs['sort_order'] = sort_order
    if not kwargs['sort_order']:
        del kwargs['sort_order']


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
# *** [LIST FACT] Options.
# ***

_cmd_options_list_fact = [
    click.option(
        '-w', '--doc', '--document', is_flag=True,
        help='Output Facts in multi-line block document format, not table.',
    ),
    click.option(
        '-r', '--rule', '--sep', nargs=1, default='',
        help=_('Separate Facts with a horizontal rule.'),
    ),
    click.option(
        '-S', '--span/--no-span', default=True, show_default=True,
        help=_('Show Fact elapsed time.'),
    ),
]


def cmd_options_list_fact(func):
    for option in reversed(_cmd_options_list_fact):
        func = option(func)
    return func


# ***
# *** [LIST ACTIVITY|LIST TAG] Options.
# ***

_cmd_options_list_categoried = [
    click.option(
        # (lb): For years, had -c/--category for the list subcommands, but
        # then I wanted to add -c/--config global option, which could work
        # because how Click parses options. But that seems confusing.
        # A -c/--config alternative could be -s/--setting?
        # Or, if you think cateGory, and that a category is much like a group,
        # then -g might seem like a reasonable shorthand for --cateGory.
        # I'll keep my eye on this... maybe -s/--setting makes more sense...
        # '-c', '--category',
        '-g', '--category',
        help=_('Restrict results by matching category name.'),
    ),
]


def cmd_options_list_categoried(func):
    for option in reversed(_cmd_options_list_categoried):
        func = option(func)
    return func


def postprocess_options_list_categoried(kwargs):
    # This little dance is so category_name is never None, but '',
    # because get_all() distinguishes between category=None and =''.
    category = kwargs['category'] if kwargs['category'] else ''
    del kwargs['category']
    return category


# ***
# *** [LIST TAG] Options.
# ***

_cmd_options_list_activitied = [
    click.option(
        '-a', '--activity',
        help=_('Restrict results by matching activity name.'),
    ),
]


def cmd_options_list_activitied(func):
    for option in reversed(_cmd_options_list_activitied):
        func = option(func)
    return func


def postprocess_options_list_activitied(kwargs):
    activity = kwargs['activity'] if kwargs['activity'] else ''
    del kwargs['activity']
    return activity


# ***
# *** [USAGE] Options.
# ***

_cmd_options_usage = [
    click.option(
        '-u', '--usage', is_flag=True,
        help=_('Include usage (just like usage command!).'),
    ),
]


def cmd_options_usage(func):
    for option in reversed(_cmd_options_usage):
        func = option(func)
    return func


class OptionWithDynamicHelp(click.Option):
    def __init__(self, *args, **kwargs):
        self.temporary_ctx = None
        super(OptionWithDynamicHelp, self).__init__(*args, **kwargs)

    @property
    def default(self):
        if not inspect.isfunction(self._default):
            return self._default
        controller = self.temporary_ctx.obj if self.temporary_ctx else None
        return self._default(controller)

    @default.setter
    def default(self, default):
        self._default = default

    def get_default(self, ctx):
        self.temporary_ctx = ctx
        df = super(OptionWithDynamicHelp, self).get_default(ctx)
        self.temporary_ctx = None
        return df

    def get_help_record(self, ctx):
        # (lb): <Ahhh'ack!> gesundheit
        self.temporary_ctx = ctx
        hr = super(OptionWithDynamicHelp, self).get_help_record(ctx)
        self.temporary_ctx = None
        return hr


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

