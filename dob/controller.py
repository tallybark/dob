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

import sys

from nark import HamsterControl

__all__ = [
    'Controller',
]


class Controller(HamsterControl):
    """
    A custom controller that adds config handling on top of its regular functionality.
    """

    def __init__(self):
        """Instantiate controller instance and adding client_config to it."""
        lib_config, client_config = get_config(get_config_instance())
        self._verify_args(lib_config)
        super(Controller, self).__init__(lib_config)
        self.client_config = client_config

    def _verify_args(self, lib_config):
        # *cough*hack!*cough*”
        # Because invoke_without_command, we allow command-less hamster
        #   invocations. For one such invocation -- murano -v -- tell the
        #   store not to log.
        # Also tell the store not to log if user did not specify anything,
        #   because we'll show the help/usage (which Click would normally
        #   handle if we hadn't tampered with invoke_without_command).
        if (
            (len(sys.argv) == 1) or
            ((len(sys.argv) == 2) and (sys.argv[1] in ('-v', 'version')))
        ):
            lib_config['sql_log_level'] = 'WARNING'
        elif len(sys.argv) == 1:
            # Because invoke_without_command, now we handle command-less
            # deliberately ourselves.
            pass

    @property
    def now(self):
        return self.store.now

