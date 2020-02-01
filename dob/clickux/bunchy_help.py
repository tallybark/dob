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

"""Module to define command group decorators and section headers."""

from gettext import gettext as _

from .help_header import help_header_format
from ..run_cli import run

__all__ = (
    'cmd_bunch_group_introducing',
    'cmd_bunch_group_edit',
    'cmd_bunch_group_get_meta',
    'cmd_bunch_group_datastore',
    'cmd_bunch_group_dbms',
    'cmd_bunch_group_add_fact',
    'cmd_bunch_group_ongoing_fact',
    'cmd_bunch_group_plugin',
)


# ***
# *** Help command group headers.
# ***

def help_header_introducing():
    return help_header_format(_('Newbie Commands'))


def help_header_edit():
    return help_header_format(_('Popular Commands'))


def help_header_get_meta():
    return help_header_format(_('Runtime Commands'))


def help_header_datastore():
    return help_header_format(_('Report Fact Commands'))


def help_header_dbms():
    return help_header_format(_('Database Commands'))


def help_header_add_fact():
    return help_header_format(_('Add Fact Commands'))


def help_header_ongoing_fact():
    return help_header_format(_('Latest Fact Commands'))


def help_header_plugin():
    return help_header_format(_('Plugin Commands'))


# ***
# *** Help command group headers.
# ***

def cmd_bunch_group_introducing(cmd):
    run.add_to_bunch(cmd, help_header_introducing, 100)
    return cmd


def cmd_bunch_group_edit(cmd):
    run.add_to_bunch(cmd, help_header_edit, 200)
    return cmd


def cmd_bunch_group_get_meta(cmd):
    run.add_to_bunch(cmd, help_header_get_meta, 600)
    return cmd


def cmd_bunch_group_datastore(cmd):
    run.add_to_bunch(cmd, help_header_datastore, 400)
    return cmd


def cmd_bunch_group_dbms(cmd):
    run.add_to_bunch(cmd, help_header_dbms, 500)
    return cmd


def cmd_bunch_group_add_fact(cmd):
    run.add_to_bunch(cmd, help_header_add_fact, 300)
    return cmd


def cmd_bunch_group_ongoing_fact(cmd):
    run.add_to_bunch(cmd, help_header_ongoing_fact, 350)
    return cmd


def cmd_bunch_group_plugin(cmd):
    run.add_to_bunch(cmd, help_header_plugin, 990)
    return cmd

