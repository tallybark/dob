# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma,  2015-2016 Eric Goller.  All rights reserved.
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

from dob.facts_format.tabular import generate_facts_table


class TestGenerateTable(object):
    def test_generate_table(self, controller_with_logging, fact):
        """Make sure the table contains all expected fact data."""
        controller = controller_with_logging
        table, columns = generate_facts_table(
            controller, [fact],
        )
        assert table[0].start == fact.start.strftime('%Y-%m-%d %H:%M')
        assert table[0].activity == fact.activity.name

    def test_generate_basic_table_column_count(self, controller_with_logging):
        """Make sure the number of table columns matches our expectation."""
        controller = controller_with_logging
        table, columns = generate_facts_table(
            controller, [],
        )
        # MAGIC_NUMBER: A basic query (without grouping or addition stats)
        # creates a table with the 8 following columns:
        #   key, start, end, activity, category, tags, description, duration
        assert len(columns) == 8

