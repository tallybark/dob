# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import editor
import six

__all__ = ['edit_fact']

def edit_fact(controller, key):
    old_fact = controller.facts.get(pk=key)

    contents = six.b(str(old_fact))
    result = editor.edit(contents=contents)

    raw_fact = result.decode()

    if old_fact.start and old_fact.end:
        time_hint = 'verify-both'
    else:
        assert old_fact.start
        time_hint = 'verify-start'

    new_fact = old_fact.create_from_raw_fact((raw_fact,), time_hint=time_hint)

    new_fact.pk = old_fact.pk

    print('An edited fact!: {}'.format(str(new_fact)))

    print('\nThe diff!\n')
    print(old_fact.friendly_diff(new_fact))

    # FIXME/2018-05-13: (lb): This is a WIP: The new Fact is not saved yet!
    #   (I want to wire it so user is prompted regarding conflicts.)

