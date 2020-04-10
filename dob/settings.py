# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

from gettext import gettext as _

from click_hotoffthehamster.exceptions import MissingParameter

from config_decorator.key_chained_val import KeyChainedValue

from dob_bright.termio import click_echo, dob_in_user_exit

from .helpers.ascii_table import generate_table

__all__ = (
    'echo_config_table',
    'echo_config_value',
    'write_config_value',
    # PRIVATE:
    #  'echo_config_value_setting',
    #  'echo_config_value_section',
    #  'exit_error_no_setting',
    #  'fetch_config_object',
    #  'fetch_config_objects',
    #  'error_exit_not_one',
    #  'config_parts_pop_value',
    #  'must_parts',
    #  'must_be_config_setting',
)


# *** [DUMP] TABLE

# FIXME/2019-11-17: BUGBUG: (lb): `-T texttable` is broken.

def echo_config_table(controller, section, keyname, **kwargs):
    """"""
    parts = list(filter(None, (section, keyname)))

    sec_key_vals = []

    def _echo_config_table():
        conf_objs = fetch_config_objects(controller, parts)
        for conf_obj in conf_objs:
            conf_obj.walk(visitor)
        echo_table()

    def visitor(condec, keyval):
        # MAYBE: Option to show hidden config.
        # MAYBE: Option to show generated config.
        if keyval.hidden:
            return

        val_def = str(keyval.value)
        if val_def != str(keyval.default):
            val_def += val_def and ' ' or ''
            val_def += encode_default(str(keyval.default))
        sec_key_vals.append((
            condec.section_path(sep='.'),
            keyval.name,
            val_def,
            keyval.doc,
        ))

    def echo_table():
        headers = (
            _("Section"),
            _("Name"),
            _("Value {}").format(encode_default(_("Default"))),
            _("Help"),
        )
        generate_table(
            sec_key_vals,
            headers,
            table_type=kwargs['table_type'],
            truncate=False,
            trunccol=0,
        )

    def encode_default(text):
        # 2019-11-30: (lb): I switched from [square brackets] to <angle brackets>
        # to avoid JSON-encoded lists being [[double bracketed]] (which triggered
        # extra mental cycles upon sight).
        return '<{}>'.format(text)

    _echo_config_table()


# *** [GET] ECHO

def echo_config_value(ctx, controller, parts):
    must_parts(ctx, parts, _('“KEYNAME”'))
    section_or_setting = fetch_config_object(controller, parts)
    if isinstance(section_or_setting, KeyChainedValue):
        echo_config_value_setting(section_or_setting)
    else:
        echo_config_value_section(section_or_setting)


def echo_config_value_setting(setting):
    click_echo(setting.value)


def echo_config_value_section(section):
    counts = []
    if section._sections:
        counts.append('{} {}'.format(len(section._sections), _('sections')))
    if section._key_vals or not section._sections:
        counts.append('{} {}'.format(len(section._key_vals), _('settings')))
    dob_in_user_exit(
        _('Configuration section “{}” contains {}.').format(
            section._name,
            _('and').join(counts),
        )
    )


# *** [SET] CONFIG

def write_config_value(ctx, controller, parts):
    parts, value = config_parts_pop_value(ctx, parts)
    section_or_setting = fetch_config_object(controller, parts)
    setting = must_be_config_setting(section_or_setting)
    try:
        setting.value = value
    except ValueError as err:
        dob_in_user_exit(str(err))
    controller.write_config(skip_unset=True)


# *** [GET/SET] FETCH

def fetch_config_object(controller, parts):
    conf_objs = fetch_config_objects(controller, parts)
    if len(conf_objs) == 1:
        return conf_objs[0]
    error_exit_not_one(parts, conf_objs)


def fetch_config_objects(controller, parts):
    try:
        conf_objs = controller.configurable.find_all(parts)
    except AttributeError:
        exit_error_no_setting(parts)
    except KeyError:
        # Raised by configurable on unknown part(s).
        exit_error_no_setting(parts)
    return conf_objs


def error_exit_not_one(parts, conf_objs):
    dotted = '.'.join(parts)
    if len(conf_objs) > 1:
        dob_in_user_exit(
            _('ERROR: Too many config objects named: “{}”').format(dotted)
        )
    else:
        # FIXME/2019-11-17 02:18: Should errors be paged if --pager?
        # - See also/Consolidate: barf_and_exit, echo_exit, dob_in_user_exit.
        dob_in_user_exit(
            _('ERROR: Not a config object: “{}”.').format(dotted)
        )


# *** [SECTION] [KEYNAME] [VALUE] VALIDATING

def config_parts_pop_value(ctx, parts):
    parts = list(parts)
    must_parts(ctx, parts, _('“KEYNAME” “VALUE”'), param_type='arguments')
    value = parts.pop()
    must_parts(ctx, parts, _('“VALUE”'))
    return parts, value


def must_parts(ctx, parts, param_hint, param_type='argument', **kwargs):
    parts = list(parts)
    if not parts:
        raise MissingParameter(
            ctx=ctx, param_hint=param_hint, param_type=param_type, **kwargs,
        )
    return parts


def must_be_config_setting(section_or_setting):
    if not isinstance(section_or_setting, KeyChainedValue):
        dob_in_user_exit(_(
            'ERROR: Not a configuration setting: “{}”.'.format(section_or_setting._name)
        ))
    return section_or_setting


def exit_error_no_setting(parts):
    dob_in_user_exit(_(
        'ERROR: Not a configuration setting: “{}”.'.format('.'.join(parts))
    ))

