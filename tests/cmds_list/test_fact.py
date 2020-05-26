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

from freezegun import freeze_time

from dob.cmds_list.fact import search_facts


from .. import truncate_to_whole_seconds


class TestSearchTerm(object):
    """Unit tests for search command."""

    @freeze_time('2015-12-12 18:00')
    def test_search(self, controller, mocker, fact, search_parameter_parametrized):
        """Ensure that search parameters are passed to appropriate backend function."""
        since, until, description, expectation = search_parameter_parametrized
        controller.facts.gather = mocker.MagicMock(return_value=[fact])
        # F841 local variable '_facts' is assigned to but never used
        _facts = search_facts(controller, since=since, until=until)  # noqa: F841
        controller.facts.gather.assert_called_with(**expectation)
        # See: nark's test_get_all_various_since_and_until_times
        assert controller.facts.gather.called
        assert controller.facts.gather.call_args[1] == {
            'since': expectation['since'],
            'until': expectation['until'],
        }

