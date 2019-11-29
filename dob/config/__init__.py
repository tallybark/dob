# -*- coding: utf-8 -*-

# This file is part of 'nark'.
#
# 'nark' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'nark' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'nark'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import datetime
import os

from gettext import gettext as _

from nark.config import ConfigRoot
from nark.config.log_levels import must_verify_log_level
from nark.config.subscriptable import Subscriptable

from ..helpers import dob_in_user_warning

from .app_dirs import AppDirs

__all__ = (
    'ConfigRoot',
    # PRIVATE:
    # 'DobConfigurableDev',
    # 'DobConfigurableEditor',
    # 'DobConfigurableFact',
    # 'DobConfigurableLog',
    # 'DobConfigurableTerm',
)


# ***
# *** Client (dob) Config.
# ***

@ConfigRoot.section('editor')
class DobConfigurableEditor(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        # See comment in NarkConfigurable:
        #   Cannot super because decorator shenanigans.
        # DEATH: super(DobConfigurableEditor, self).__init__(*args, **kwargs)
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, center the interface in the terminal (on `dob edit`)"),
    )
    def centered(self):
        return False

    # ***

    @property
    @ConfigRoot.setting(
        # FIXME/2019-11-18: Confirm Pygments lexer, does it work, is it wired?
        _("Fact lexer. Defaults to Pygments lexer."),
        # FIXME/2019-11-16 22:45: Confirm hidden option!
        hidden=True,
    )
    def lexer(self):
        return ''

    # ***

    @property
    @ConfigRoot.setting(
        _("Interface style to use."),
    )
    def styling(self):
        return ''


# ***

@ConfigRoot.section('fact')
class DobConfigurableFact(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("Separator character(s) using to indicate datetime start to end."),
    )  # noqa: E501
    def separators(self):
        return ''


# ***

@ConfigRoot.section('dev')
class DobConfigurableDev(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("The log level for frontend (dob) squaller"
            " (using Python logging library levels)"),
        # MEH/2019-01-17: We should warn, not die; see: resolve_log_level.
        validate=must_verify_log_level,
    )
    def cli_log_level(self):
        return 'WARNING'

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, enables features for developing dob"
            " (e.g., stop at REPL on affirm faults)."),
    )
    def catch_errors(self):
        return False


# ***

@ConfigRoot.section('log')
class DobConfigurableLog(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("Filename of dob log under AppDirs.user_log_dir"),
    )
    def filename(self):
        return 'dob.log'

    # ***

    # User should not set logfile_path in config, because it's
    # generated, but we make it a pseudo-setting so the code can
    # access just the same as other settings (and the value depends
    # on another config value, the log_filename, so it sorta is a
    # config value, just a derived one).
    @property
    @ConfigRoot.setting(
        _('Generate value.'),
        ephemeral=True,
    )
    def filepath(self):
        log_dir = AppDirs.user_log_dir
        # Note that self is the root ConfigDecorator, not the DobConfigurableLog...
        log_filename = self['filename']
        return os.path.join(log_dir, log_filename)

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, use color in log files (useful if tailing logs in terminal)"),
    )
    def use_color(self):
        return False

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, send logs to the console, not the file"),
    )
    def use_console(self):
        return True


# ***

@ConfigRoot.section('term')
class DobConfigurableTerm(Subscriptable):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("Path to directory where export files are created"),

        # FIXME/2019-11-17 00:56: Nothing uses export_path.
        #   So hidden for now. Delete later, or implement.
        hidden=True,
    )
    def export_path(self):
        """
        Return path to save exports to.
        File extension will be added by export method.
        """
        # FIXME: Not sure who this'll be used... maybe two separate config
        #        values, one editable and one generated, like log_filename
        #        and logfile_path. But first, we need a feature that exports!
        #        Until then... either keep this setting hidden, or delete it!
        return os.path.join(AppDirs.user_data_dir, 'export')

    # ***

    @property
    @ConfigRoot.setting(
        _("The filename suffix to tell EDITOR so it can determine highlighting"),
    )
    def editor_suffix(self):
        return ''

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, show copyright greeting before every command."),
    )
    def show_greeting(self):
        return False

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, use color and font ornamentation in output."),
    )
    def use_color(self):
        return True

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, send application output to terminal pager."),
    )
    def use_pager(self):
        return False

