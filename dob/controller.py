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

"""The Controller."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click
import os
import sys

from nark import HamsterControl

from . import help_strings
from .copyright import echo_copyright
from .cmd_config import get_config_path, furnish_config, replenish_config
from .helpers import dob_in_user_exit
from .migrate import upgrade_legacy_database_instructions

# Disable the python_2_unicode_compatible future import warning.
click.disable_unicode_literals_warning = True

__all__ = [
    'Controller',
]

# ***
# *** [CONTROLLER] HamsterControl Controller.
# ***


class Controller(HamsterControl):
    """
    A custom controller that adds config handling on top of its regular functionality.
    """

    def __init__(self):
        """Load backend and client configs, and instantiate controller."""
        nark_config, dob_config, preexists = furnish_config()
        self._adjust_log_level(nark_config)
        super(Controller, self).__init__(nark_config)
        self.client_config = dob_config
        self.cfgfile_exists = preexists

    def create_config(self, force):
        exists = os.path.exists(get_config_path())
        if exists and not force:
            dob_in_user_exit('Config file exists')
        nark_config, dob_config, file_path = replenish_config()
        self._adjust_log_level(nark_config)
        self.config = nark_config
        self.client_config = dob_config
        click.echo(
            _('Initialized default Dob configuration at {}').format(file_path)
        )

    @property
    def store_exists(self):
        # Check either db_path is set, or all of db_host/_port/_name/_user.
        if self.config['db_engine'] == 'sqlite':
            return os.path.isfile(self.config['db_path'])
        else:
            return bool(self.store.get_db_url())

    def _adjust_log_level(self, nark_config):
        # *cough*hack!*cough*”
        # Because invoke_without_command, we allow command-less invocations.
        #   For one such invocation -- dob -v -- tell the store not to log.
        # Also tell the store not to log if user did not specify anything,
        #   because we'll show the help/usage (which Click would normally
        #   handle if we had not tampered with invoke_without_command).
        if (
            (len(sys.argv) > 2) or
            ((len(sys.argv) == 2) and (sys.argv[1] not in ('-v', 'version')))
        ):
            return
        nark_config['sql_log_level'] = 'WARNING'

    @property
    def now(self):
        return self.store.now

