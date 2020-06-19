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

from dob_bright.termio import ascii_table

from dob import cmds_list


class TestActivities(object):
    """Unit tests for the ``activities`` command."""

    def test_tabulate_list_activities_no_category(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure command works if activities do not have a category associated."""
        activity.category = None
        mocker.patch.object(
            controller.activities, 'get_all', return_value=[activity],
        )
        mocker.patch.object(
            ascii_table.tabulate,
            'tabulate',
            return_value='{}, {}'.format(activity.name, None),
        )
        cmds_list.activity.list_activities(
            controller,
            output_format='table',
            # Specify any one of 'tabulate' types.
            table_type='rst',
        )
        out, err = capsys.readouterr()
        assert out.startswith(activity.name)
        assert ascii_table.tabulate.tabulate.call_args[0] == ([(activity.name, None)],)

    def test_list_activities_no_category(self, controller, activity, mocker, capsys):
        """Make sure command works if activities do not have a category associated."""
        activity.category = None
        mocker.patch.object(
            controller.activities, 'get_all', return_value=[activity],
        )
        mocker.patch.object(ascii_table.texttable.Texttable, 'add_rows')
        mocker.patch.object(
            ascii_table.texttable.Texttable,
            'draw',
            return_value='{}, {}'.format(activity.name, None),
        )
        cmds_list.activity.list_activities(
            controller,
            output_format='table',
            table_type='texttable',
        )
        out, err = capsys.readouterr()
        assert out.startswith(activity.name)
        add_rows_call_args = ascii_table.texttable.Texttable.add_rows.call_args
        # The first row is the headers. Second row is activity, category passed.
        assert add_rows_call_args[0][0][1] == (activity.name, None)
        draw_call_args = ascii_table.texttable.Texttable.draw.call_args
        assert draw_call_args[0] == ()

    def test_list_activities_no_filter(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure activity name and category are displayed if present."""
        mocker.patch.object(
            controller.activities, 'get_all', return_value=[activity],
        )
        cmds_list.activity.list_activities(controller)
        out, err = capsys.readouterr()
        assert activity.name in out
        assert activity.category.name in out

    def test_list_activities_using_category(
        self, controller, activity, mocker, capsys,
    ):
        """Make sure the search term is passed on."""
        mocker.patch.object(
            controller.activities, 'query_process_results', return_value=[activity],
        )
        mocker.patch.object(
            controller.activities,
            'query_filter_by_category_name',
            return_value=activity.category.name,
        )
        cmds_list.activity.list_activities(
            controller,
            match_categories=[activity.category],
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
        mocker.patch.object(
            controller.activities, 'gather', return_value=[activity],
        )
        cmds_list.activity.list_activities(
            controller,
            # Defaults.
            output_format='table',
            show_usage=True,
            show_duration=True,
            # The one we're testing.
            search_terms=[activity.category.name],
        )
        out, err = capsys.readouterr()
        assert controller.activities.gather.called
        # Mock's assert_called_with checks arguments exactly, but we
        # just care to check that the search_term was there.
        query_terms = controller.activities.gather.call_args[0][0]
        assert query_terms.search_terms == [activity.category.name]
        # The category is a pass-through list_activities **kwarg, so
        # won't be in the kwargs.
        assert query_terms.match_categories == []
        assert activity.name in out
        assert activity.category.name in out

