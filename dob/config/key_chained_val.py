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

from gettext import gettext as _

import os

__all__ = (
    'KeyChainedValue',
)


class KeyChainedValue(object):
    def __init__(
        self,
        section=None,
        name='',
        default_f=None,
        value_type=None,
        # Optional.
        choices='',
        doc='',
        ephemeral=False,
        hidden=False,
        validate=None,
    ):
        self._section = section
        self._name = name
        self._default_f = default_f
        self._choices = choices
        self._doc = doc
        self._ephemeral = ephemeral
        self._hidden = hidden
        self._validate_f = validate

        self._value_type = self.deduce_value_type(value_type)

        # These attributes will only be set if some particular
        # source specifies a value:
        #  self._val_forced
        #  self._val_cliarg
        #  self._val_envvar
        #  self._val_config

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default_f(self._section)

    def deduce_value_type(self, value_type=None):
        if self.ephemeral or value_type is not None:
            return value_type
        elif isinstance(self.default, bool):
            return bool
        elif isinstance(self.default, int):
            return int
        return str

    @property
    def doc(self):
        return self._doc

    @property
    def ephemeral(self):
        if callable(self._ephemeral):
            if self._section is None:
                return False
            return self._ephemeral(self)
        return self._ephemeral

    def _find_root(self):
        return self._section._find_root()

    @property
    def hidden(self):
        if callable(self._hidden):
            if self._section is None:
                return False
            return self._hidden(self)
        return self._hidden

    @property
    def persisted(self):
        return hasattr(self, '_val_config')

    def _typify(self, value):
        if self._value_type is bool:
            if value == 'True':
                return True
            elif value == 'False':
                return False
        return self._value_type(value)

    def _walk(self, visitor):
        visitor(self._section, self)

    # ***

    @property
    def value(self):
        # Honor forced values foremost.
        try:
            return self.value_from_forced
        except AttributeError:
            pass
        # Honor CLI-specific values secondmost.
        try:
            return self.value_from_cliarg
        except AttributeError:
            pass
        # Check the environment third.
        try:
            return self.value_from_envvar
        except KeyError:
            pass
        # See if the config value was specified by the config that was read.
        try:
            return self.value_from_config
        except AttributeError:
            pass
        # Nothing found so far! Finally just return the default value.
        return self.default

    @value.setter
    def value(self, value):
        value = self.value_cast_and_validate(value)
        # Using the `value =` shortcut, or using `section['key'] = `,
        # is provided as a convenient way to inject values from the
        # config file, or that the user wishes to set in the file.
        # If the caller wants to just override the value, consider
        # setting self.value_from_forced instead.
        self.value_from_config = value

    def value_cast_and_validate(self, value):
        value = self._typify(value)
        invalid = False
        addendum = ''
        if self._validate_f:
            if not self._validate_f(value):
                invalid = True
        elif self._choices:
            if value not in self._choices:
                invalid = True
                addendum = _(' (Choose from: ‘{}’)').format('’, ‘'.join(self._choices))
        if invalid:
            raise ValueError(
                _("Unrecognized value for setting ‘{}’: “{}”{}").format(
                    self._name, value, addendum,
                ),
            )
        return value

    # ***

    @property
    def value_from_forced(self):
        return self._val_forced

    @value_from_forced.setter
    def value_from_forced(self, value_from_forced):
        self._val_forced = self._typify(value_from_forced)

    # ***

    @property
    def value_from_cliarg(self):
        return self._val_cliarg

    @value_from_cliarg.setter
    def value_from_cliarg(self, value_from_cliarg):
        self._val_cliarg = self._typify(value_from_cliarg)

    # ***

    @property
    def value_from_envvar(self):
        environame = 'DOB_{}_{}'.format(
            self._section._section_path(sep='_').upper(),
            self._name.upper(),
        )
        envval = os.environ[environame]
        envval = self.value_cast_and_validate(envval)
        return envval

    # ***

    @property
    def value_from_config(self):
        return self._val_config

    @value_from_config.setter
    def value_from_config(self, value_from_config):
        self._val_config = self._typify(value_from_config)

    def forget_config_value(self):
        try:
            del self._val_config
        except AttributeError:
            pass


