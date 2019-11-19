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

__all__ = (
    'Subscriptable',
)


class Subscriptable(object):
    """"""

    def __init__(self):
        super(Subscriptable, self).__init__()
        pass

    def __getitem__(self, name):
        """Makes object[subscripting] to same-named object.attribute.
           E.g., user can access data at `obj['key']` as well as `obj.key`.
        """
        item = getattr(self, name)
        try:
            return item.value
        except AttributeError:
            return item

