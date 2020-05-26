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

import pytest

from dob_bright.termio import ascii_table

from dob import cmds_list


class TestActivities(object):
    """Unit tests for the ``activities`` command."""

    def test_list_activities_no_category(self, controller, activity, mocker, capsys):
        """Make sure command works if activities do not have a category associated."""
        activity.category = None
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        ascii_table.tabulate.tabulate = mocker.MagicMock(
            return_value='{}, {}'.format(activity.name, None),
        )
        cmds_list.activity.list_activities(controller, table_type='tabulate')
        out, err = capsys.readouterr()
        assert out.startswith(activity.name)
        assert ascii_table.tabulate.tabulate.call_args[0] == ([[activity.name, None]],)

    def test_list_activities_no_filter(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure activity name and category are displayed if present."""
        controller.activities.get_all = mocker.MagicMock(
            return_value=[activity],
        )
        cmds_list.activity.list_activities(controller, '')
        out, err = capsys.readouterr()
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_using_category(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        controller.activities.query_process_results = mocker.MagicMock(
            return_value=[activity],
        )
        controller.activities.query_filter_by_category_name = mocker.MagicMock(
            return_value=activity.category.name,
        )
        cmds_list.activity.list_activities(
            controller, category=activity.category,
        )
        out, err = capsys.readouterr()
        assert controller.activities.query_filter_by_category_name.called
        controller.activities.query_filter_by_category_name.assert_called_with(
            activity.category,
        )
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_with_search_term(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        controller.activities.gather = mocker.MagicMock(
            return_value=[activity],
        )
        cmds_list.activity.list_activities(
            controller,
            # Defaults.
            table_type='friendly',
            chop=False,
            hide_usage=False,
            hide_duration=False,
            # The one we're testing.
            search_term=activity.category.name,
        )
        out, err = capsys.readouterr()
        assert controller.activities.gather.called
        # Mock's assert_called_with checks arguments exactly, but we
        # just care to check that the search_term was there.
        assert (
            controller.activities.gather.call_args.kwargs['search_term']
            == activity.category.name
        )
        # The category is a pass-through list_activities **kwarg, so
        # won't be in the kwargs.
        assert 'category' not in controller.activities.gather.call_args.kwargs
        assert activity.name in out
        assert activity.category.name in out

    # (lb): This test made more sense in hamster-lib, where you could pass a Category
    # item to the Activity get_all. But in dob, it bakes the Category search into
    # the SQL, so there's not gonna be a KeyError or anything raised on an unknown
    # Category name. Also, the test does not setup the database here, so the SQL
    # won't not find anything because the Category name is a miss, it just won't
    # find anything because there's nothing in the database.
    # See instead:
    #   nark.tests.backends.sqlalchemy.test_storage.test_get_all_with_category_miss
    if False:
        def test_list_activities_with_category_miss(
            self, controller, activity, mocker, capsys,
        ):
            """Make sure the search term is passed on."""
            category_miss = activity.category.name + '_test'
            controller.activities.get_all = mocker.MagicMock(
                return_value=[activity],
            )
            with pytest.raises(KeyError):
                cmds_list.activity.list_activities(
                    controller, filter_category=category_miss,
                )
                assert False  # Unreachable.
            out, err = capsys.readouterr()
            assert not controller.activities.get_all.called

