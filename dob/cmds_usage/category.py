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

from __future__ import absolute_import, unicode_literals

from . import generate_usage_table

__all__ = ['usage_categories']


def usage_categories(
    controller,
    table_type='friendly',
    truncate=False,
    **kwargs
):
    """
    List all categories' usage counts, with filtering and sorting options.

    Returns:
        None: If success.
    """
    results = controller.categories.get_all_by_usage(**kwargs)
    generate_usage_table(results, table_type=table_type, truncate=truncate)
