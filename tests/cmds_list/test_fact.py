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
import pytest

from nark.tests.conftest import *
from nark.tests.backends.sqlalchemy.conftest import *

from dob_viewer.crud.fact_dressed import FactDressed
from dob.cmds_list.fact import list_facts
from dob.cmds_list.fact import search_facts
from dob.facts_format.tabular import report_table_columns


class TestCmdsListFactSearchFacts(object):
    """Unit tests for search command."""

    @freeze_time('2015-12-12 18:00')
    def test_search_facts_since_until(
        self, controller, mocker, fact, search_parameter_parametrized,
    ):
        """Ensure since and until are converted to datetime for backend function."""
        # See also: nark's test_get_all_various_since_and_until_times
        since, until, description, expectation = search_parameter_parametrized
        mocker.patch.object(controller.facts, 'gather', return_value=[fact])
        # F841 local variable '_facts' is assigned to but never used
        _facts = search_facts(controller, since=since, until=until)  # noqa: F841
        assert controller.facts.gather.called
        # call_args is (args, kwargs), and QueryTerms is the first args arg.
        query_terms = controller.facts.gather.call_args[0][0]
        assert query_terms.since == expectation['since']
        assert query_terms.until == expectation['until']

    def test_search_facts_fails_on_unsupported_store(self, controller, capsys):
        """Ensure search_facts prints a user warning on unsupported store type."""
        # MAYBE/2020-05-26: Add support for other data stores (other than SQLite),
        #   which requires using and wiring the appropriate DBMS-specific aggregate
        #   functions.
        #   - For now, dob is at least nice enough to print an error message.
        controller.store.config['db.engine'] += '_not'
        with pytest.raises(SystemExit):
            search_facts(controller)
            assert False  # Unreachable.
        # assert result.exit_code == 1
        out, err = capsys.readouterr()
        # See: must_support_db_engine_funcs.
        expect = 'This feature does not work with the current DBMS engine'
        assert err.startswith(expect)


# ***

class TestCmdsListFactListFacts(object):
    """"""

    def test_list_facts_empty_store(self, controller_with_logging, capsys):
        """..."""
        controller = controller_with_logging
        with pytest.raises(SystemExit):
            list_facts(
                controller,
            )
            assert False  # Unreachable.
        out, err = capsys.readouterr()
        # See: error_exit_no_results.
        expect = 'No facts were found for the specified query.'
        assert err.startswith(expect)

    # ***

    def test_list_facts_basic_store(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        capsys,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        list_facts(controller)
        out, err = capsys.readouterr()
        assert not err
        # We could verify the report looks like how we expect, but that seems
        # better suited for using a snapshots feature. It would be painful to
        # maintain here, especially as the report formats evolve.
        assert out


# ***

# Mostly coverage of
#   dob/cmds_list/fact.py
# but also provides coverage of
#   dob/facts_format/factoid.py

class TestCmdsListFactListFactsPresentationArguments(object):

    # We're just going for coverage and not crashing, so not checking test outputs.

    # ***

    @pytest.mark.parametrize(
        ('include_stats', 'hide_usage', 'hide_duration', 'hide_description',), (
            (True, True, True, True),
        )
    )
    def test_list_facts_hide_hide_hide(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        include_stats,
        hide_usage,
        hide_duration,
        hide_description,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        list_facts(
            controller,
            include_stats=include_stats,
            hide_usage=hide_usage,
            hide_duration=hide_duration,
            hide_description=hide_description,
        )

    # ***

    def test_list_facts_custom_columns_all_columns(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        # See also: FACT_TABLE_HEADERS.
        custom_columns = report_table_columns()
        list_facts(controller, column=custom_columns)

    # ***

    # For reference:
    #
    #   REPORT_COLUMNS_DEFAULT = [
    #       'key',
    #       'start',
    #       'end',
    #       'activity',
    #       'category',
    #       'tags',
    #       'description',
    #       'duration',
    #   ]

    def test_list_facts_custom_columns_a_few_columns_group_activity(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        custom_columns = ['activity', 'duration']
        list_facts(controller, column=custom_columns, group_activity=True)

    # ***

    @pytest.mark.parametrize(
        ('format_journal', 'format_tabular', 'format_factoid', 'table_type',), (
            (False, True, False, 'friendly'),
            (False, True, False, 'texttable'),
            (False, True, False, 'tabulate'),
            (False, False, True, '*ignored*'),
            (True, False, False, '*ignored*'),
        )
    )
    def test_list_facts_format_permutations(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        format_journal,
        format_tabular,
        format_factoid,
        table_type,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        # Ensure that fact.friendly_str() is the FactDressed version
        # (because Factoid format uses 'colorful' argument).
        controller.store.fact_cls = FactDressed
        list_facts(
            controller,
            format_journal=format_journal,
            format_tabular=format_tabular,
            format_factoid=format_factoid,
            table_type=table_type,
        )

    # ***

    @pytest.mark.parametrize(
        ('spark_total', 'spark_width', 'spark_secs',), (
            ('', None, None),
            ('max', None, None),
            ('net', None, None),
            (100, None, None),
            (None, 24, None),
            (None, None, 3600),
        )
    )
    def test_list_facts_format_jounrnal_spark_args(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        spark_total,
        spark_width,
        spark_secs,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        list_facts(
            controller,
            format_journal=True,
            spark_total=spark_total,
            spark_width=spark_width,
            spark_secs=spark_secs,
        )

    # ***

    @pytest.mark.parametrize(
        ('format_tabular', 'format_factoid',), (
            (True, False),
            (False, True),
        )
    )
    def test_list_facts_chop(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        format_tabular,
        format_factoid,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        list_facts(
            controller,
            chop=True,
            format_tabular=format_tabular,
            format_factoid=format_factoid,
        )

    # ***

    def test_list_facts_sort_cols(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        sort_cols = ('activity', 'start')
        list_facts(controller, sort_cols=sort_cols)

    # ***


# ***

class TestCmdsListFactFactoidPermutations(object):

    # We're just going for coverage and not crashing, so not checking test outputs.

    # ***

    def test_list_facts_format_factoid_factoid_rule(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        factoid_rule = '++rule-this++'
        list_facts(
            controller,
            format_factoid=True,
            factoid_rule=factoid_rule,
        )

    # ***

    def test_list_facts_format_factoid_out_file(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        mocker,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        out_file = mocker.MagicMock()
        list_facts(
            controller,
            format_factoid=True,
            out_file=out_file,
        )
        assert out_file.write.called

    # ***

    @pytest.mark.parametrize(
        ('format_tabular', 'format_factoid', 'row_limit'), (
            (True, False, 2),
            (False, True, 2),
        )
    )
    def test_list_facts_format_factoid_row_limit(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        format_tabular,
        format_factoid,
        row_limit,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        list_facts(
            controller,
            format_tabular=format_tabular,
            format_factoid=format_factoid,
            row_limit=row_limit,
        )

    # ***

    def test_list_facts_format_factoid_term_width(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        term_width = 40
        list_facts(
            controller,
            format_factoid=True,
            chop=True,
            term_width=term_width,
        )

    # ***

    def test_list_facts_format_factoid_and_chop_isatty_uses_term_size(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
        mocker,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        controller.store.fact_cls = FactDressed
        isatty = mocker.patch('sys.stdout.isatty', return_value=True)
        get_ts = mocker.patch(
            'click_hotoffthehamster.get_terminal_size', return_value=(80, 24),
        )
        list_facts(
            controller,
            format_factoid=True,
            chop=True,
        )
        assert isatty.called
        assert get_ts.called

    # ***

    def test_list_facts_format_factoid_grouping_not_allowed(
        self,
        alchemy_store,
        set_of_alchemy_facts,
        controller_with_logging,
    ):
        controller = controller_with_logging
        controller.store = alchemy_store
        with pytest.raises(SystemExit):
            list_facts(
                controller,
                format_factoid=True,
                group_days=True,
            )
            assert False  # Unreachable.

