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

import inspect
from collections import OrderedDict
from functools import update_wrapper

from gettext import gettext as _

from .key_chained_val import KeyChainedValue
from .subscriptable import Subscriptable
from ..helpers import dob_in_user_warning

__all__ = (
    'section',
    # PRIVATE:
    # 'ConfigDecorator',
)


class ConfigDecorator(Subscriptable):
    def __init__(self, cls, cls_or_name, *args, parent=None, **kwargs):
        super(ConfigDecorator, self).__init__(*args, **kwargs)

        self._defaults = cls()

        self._parent = parent

        self._kv_cache = OrderedDict()
        self._key_vals = {}

        self._sections = OrderedDict()

        if isinstance(cls_or_name, str):
            self._name = cls_or_name
        else:
            self._name = cls.__name__

        if parent is not None:
            self._pull_kv_cache(parent)

        self._initialized = True

    def _pull_kv_cache(self, parent):
        # The decorators ran against the parent object,
        # so steal its settings cache.
        self._key_vals = parent._kv_cache
        parent._kv_cache = OrderedDict()
        # And fix the settings from the parent cache to
        # now reference this object as the owner.
        for kval in self._key_vals.values():
            kval._section = self
        # Finally update the parent and register this
        # object as a section.
        parent._sections[self._name] = self

    def update_from_dict(self, config):
        for section, conf_dtor in self._sections.items():
            if section in config:
                conf_dtor.update_from_dict(config[section])
        for name, ckv in self._key_vals.items():
            if ckv.ephemeral:
                # Essentially unreachable, unless hacked config file.
                continue
            if name in config:
                try:
                    ckv.value = config[name]
                except ValueError as err:
                    dob_in_user_warning(str(err))
        return self

    def download_to_dict(
        self, config, skip_unset=False, use_defaults=False, add_hidden=False,
    ):
        def _download_to_dict():
            n_settings = 0
            for section, conf_dtor in self._sections.items():
                n_settings += _recurse_section(section, conf_dtor)
            for name, ckv in self._key_vals.items():
                if ckv.ephemeral:
                    continue
                try:
                    config[name] = choose_default_or_confval(ckv)
                    n_settings += 1
                except AttributeError:
                    pass
            return n_settings

        def _recurse_section(section, conf_dtor):
            existed = section in config
            subsect = config.setdefault(section, {})
            n_settings = conf_dtor.download_to_dict(subsect)
            if not n_settings and not existed:
                del config[section]
            return n_settings

        def choose_default_or_confval(ckv):
            if (
                (use_defaults or (not ckv.persisted and not skip_unset))
                and (not ckv.hidden or add_hidden)
            ):
                return ckv.default
            elif not use_defaults and ckv.persisted:
                return ckv.value_from_config
            raise AttributeError()

        return _download_to_dict()

    def _section_path(self, parts=None, sep='_'):
        if parts is None:
            parts = []
        # Ignore the root element. Start with its sections.
        if self._parent is None:
            return sep.join(parts)
        parts.insert(0, self._name)
        return self._parent._section_path(parts, sep)

    def _walk(self, visitor):
        for keyval in self._key_vals.values():
            visitor(self, keyval)
        for conf_dtor in self._sections.values():
            conf_dtor._walk(visitor)

    def _find(self, parts, skip_sections=False):
        # If caller specifies just one part, we'll do a loose, lazy match.
        # Otherwise, if parts is more than just one entry, look for exact.
        # - This supports use case of user being lazy, e.g., `dob get tz_aware`,
        #   but also prevents problems being lazy-exact, e.g., `dob get abc xyz`
        #   should be precise and return only abc.xyz, and not, say, zbc.def.xyz.

        def _find_objects():
            if not parts:
                return [self]
            elif len(parts) == 1:
                objects = self._find_objects_named(parts[0], skip_sections)
            else:
                section_names = parts[:-1]
                object_name = parts[-1]

                conf_dtor = self
                for name in section_names:
                    conf_dtor = conf_dtor._sections[name]

                objects = []
                if object_name in conf_dtor._sections and not skip_sections:
                    objects.append(conf_dtor._sections[object_name])
                if object_name in conf_dtor._key_vals:
                    objects.append(conf_dtor._key_vals[object_name])

            return objects

        return _find_objects()

    def _find_objects_named(self, name, skip_sections=False):
        objects = []
        if name in self._sections and not skip_sections:
            objects.append(self._sections[name])
        if name in self._key_vals:
            objects.append(self._key_vals[name])
        for section, conf_dtor in self._sections.items():
            objects.extend(conf_dtor._find_objects_named(name, skip_sections))
        return objects

    def _find_root(self):
        if not self._parent:
            return self
        return self._parent._find_root()

    def _find_setting(self, parts):
        objects = self._find(parts, skip_sections=True)
        if objects:
            return objects[0]
        return None

    def forget_config_values(self):
        def visitor(condec, keyval):
            keyval.forget_config_value()
        self._walk(visitor)

    # A @redecorator.
    def section(self, name):
        return section(name, parent=self)

    def setting(self, message=None, **kwargs):
        def decorator(func):
            kwargs.setdefault('name', func.__name__)
            doc = message
            if doc is None:
                doc = func.__doc__
            ckv = KeyChainedValue(
                default_f=func,
                doc=doc,
                # self is parent section; we'll set later.
                section=None,
                **kwargs
            )
            self._kv_cache[ckv.name] = ckv

            def _decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return update_wrapper(_decorator, func)
        return decorator

    def setdefault(self, name, value):
        # To appease nark, quack like a duck (dict) and implement setdefault,
        # which nark calls to make sure all the config settings it cares about
        # are setup.
        if name in self._key_vals:
            return
        ckv = KeyChainedValue(
            name,
            default_f=lambda x: value,
            doc=_('Error: Missing default'),
            section=self,
        )
        self._key_vals[ckv.name] = ckv

    def __getattr__(self, name):
        return self._find_one_object(name)

    def _find_one_object(self, name):
        objects = self._find_objects_named(name)
        if len(objects) > 1:
            dob_in_user_warning(
                _('More than one config object named: “{}”').format(name)
            )
        if objects:
            return objects[0]
        else:
            # Unexpected branch. Because __getattr__ only called if explicit
            # attribute not found (i.e., we didn't set it in, e.g., init()),
            # and such attributes should be known config section...
            # WAIT maybe on dob-config-get-BLAH it'll fail...
            dob_in_user_warning(
                _('Unexpected code path: {}.__get__attr__(name="{}")').format(
                    self.__class__.__name__, name,
                )
            )
            return super(ConfigDecorator, self).__getattribute__(name)

    def __setitem__(self, name, value):
        self._find_one_object(name).value = value


# Note that Python invokes the decorator with the item being decorated. If
# you want to pass arguments to the decorator, you can call a function to
# retain the arguments and to generate the actual decorator .
#
# E.g., if a decorator is not explicitly invoked,
#
#   @section
#   class SomeClass(object):
#       ...
#
# then the argument to the decorator is the SomeClass object. Python executes
# the decorator with the object being decorated, in this case a class.
#
# Otherwise, if a decorator is invoked upon decoration, e.g.,
#
#   @section('SectionName')
#   class SomeClass(object):
#       ...
#
# then the method being invoked must return the actual decorator.
#
# Here we support either approach.
def section(cls_or_name, parent=None):
    def _add_section(cls, *args, **kwargs):
        return ConfigDecorator(cls, cls_or_name, parent=parent, *args, **kwargs)

    if inspect.isclass(cls_or_name):
        # The decorator was used without being invoked first, e.g.,
        #   @section
        #   class Classy...
        _add_section(cls_or_name)
        return cls_or_name
    else:
        # The decorator was invoked first with arguments, so return the
        # actual decorator which Python will call back immediately with
        # the class being decorated.
        return _add_section

