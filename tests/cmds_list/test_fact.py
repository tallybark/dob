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

import os

import fauxfactory
import pytest

import nark
from nark.tests.conftest import *  # noqa: F401, F403
from nark.tests.backends.sqlalchemy.conftest import *  # noqa: F401, F403

from dob_bright.crud.fact_dressed import FactDressed
from dob_bright.reports.tabulate_results import report_table_columns

from dob.cmds_list.fact import list_facts

from .. import truncate_to_whole_seconds


# ***

class TestCmdsListFactListFacts_Simple(object):
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
        five_report_facts_ctl,
        capsys,
    ):
        controller = five_report_facts_ctl
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

class TestCmdsListFactListFacts_PresentationArguments(object):

    # We're just going for coverage and not crashing, so not checking test outputs.

    # ***

    @pytest.mark.parametrize(
        ('include_stats', 'show_usage', 'show_duration', 'hide_description',), (
            (True, True, True, True),
        )
    )
    def test_list_facts_show_show_hide(
        self,
        five_report_facts_ctl,
        include_stats,
        show_usage,
        show_duration,
        hide_description,
    ):
        controller = five_report_facts_ctl
        list_facts(
            controller,
            include_stats=include_stats,
            show_usage=show_usage,
            show_duration=show_duration,
            hide_description=hide_description,
        )

    # ***

    def test_list_facts_custom_columns_all_columns(
        self,
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
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
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
        custom_columns = ['activity', 'duration']
        list_facts(controller, column=custom_columns, group_activity=True)

    # ***

    @pytest.mark.parametrize(
        ('output_format', 'table_type',), (
            ('table', 'normal'),
            ('table', 'rst'),
            ('factoid', '*ignored*'),
            ('journal', '*ignored*'),
        )
    )
    def test_list_facts_format_permutations(
        self,
        five_report_facts_ctl,
        output_format,
        table_type,
    ):
        controller = five_report_facts_ctl
        # Ensure that fact.friendly_str() is the FactDressed version
        # (because Factoid format uses 'colorful' argument).
        controller.store.fact_cls = FactDressed
        list_facts(
            controller,
            output_format=output_format,
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
        five_report_facts_ctl,
        spark_total,
        spark_width,
        spark_secs,
    ):
        controller = five_report_facts_ctl
        list_facts(
            controller,
            output_format='journal',
            spark_total=spark_total,
            spark_width=spark_width,
            spark_secs=spark_secs,
        )

    # ***

    @pytest.mark.parametrize(
        ('output_format',), (
            ('table',),
            ('factoid',),
        )
    )
    def test_list_facts_max_width(
        self,
        five_report_facts_ctl,
        output_format,
    ):
        controller = five_report_facts_ctl
        list_facts(
            controller,
            output_format=output_format,
            max_width=80,
        )

    # ***

    def test_list_facts_sort_cols(
        self,
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
        sort_cols = ('activity', 'start')
        list_facts(controller, sort_cols=sort_cols)

    # ***


# ***

class TestCmdsListFactListFacts_FactoidPermutations(object):

    # We're just going for coverage and not crashing, so not checking test outputs.

    # ***

    def test_list_facts_output_format_factoid_factoid_rule(
        self,
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
        factoid_rule = '++rule-this++'
        list_facts(
            controller,
            output_format='factoid',
            factoid_rule=factoid_rule,
        )

    # ***

    def test_list_facts_output_format_factoid_output_path(
        self,
        five_report_facts_ctl,
        mocker,
    ):
        controller = five_report_facts_ctl
        output_path = mocker.MagicMock()
        list_facts(
            controller,
            output_format='factoid',
            output_path=output_path,
        )
        assert output_path.write.called

    # ***

    @pytest.mark.parametrize(
        ('output_format', 'row_limit'), (
            ('table', 2),
            ('factoid', 2),
        )
    )
    def test_list_facts_output_format_factoid_row_limit(
        self,
        five_report_facts_ctl,
        output_format,
        row_limit,
    ):
        controller = five_report_facts_ctl
        list_facts(
            controller,
            output_format=output_format,
            row_limit=row_limit,
        )

    # ***

    def test_list_facts_output_format_factoid_max_width(
        self,
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
        max_width = 40
        list_facts(
            controller,
            output_format='factoid',
            max_width=max_width,
        )

    # ***

    def test_list_facts_output_format_factoid_and_chop_isatty_uses_term_size(
        self,
        five_report_facts_ctl,
        mocker,
    ):
        controller = five_report_facts_ctl
        isatty = mocker.patch('sys.stdout.isatty', return_value=True)
        get_ts = mocker.patch(
            'click_hotoffthehamster.get_terminal_size', return_value=(80, 24),
        )
        list_facts(
            controller,
            output_format='table',
            max_width=None,
        )
        assert isatty.called
        assert get_ts.called

    # ***

    def test_list_facts_output_format_factoid_grouping_not_allowed(
        self,
        five_report_facts_ctl,
    ):
        controller = five_report_facts_ctl
        with pytest.raises(SystemExit):
            list_facts(
                controller,
                output_format='factoid',
                group_days=True,
            )
            assert False  # Unreachable.


# ***

class TestCmdsListFactListFacts_OutputFormats(object):
    """Unittests related to data export."""
    @pytest.mark.parametrize('output_format', ['soap', fauxfactory.gen_latin1()])
    def test_invalid_format(self, five_report_facts_ctl, output_format, mocker):
        """Make sure that passing an invalid format exits prematurely."""
        controller = five_report_facts_ctl
        with pytest.raises(Exception):
            list_facts(controller, output_format=output_format)

    def test_csv(self, five_report_facts_ctl, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        mocker.patch.object(nark.reports.csv_writer.CSVWriter, 'write_facts')
        controller = five_report_facts_ctl
        list_facts(controller, output_format='csv')
        assert nark.reports.csv_writer.CSVWriter.write_facts.called

    def test_tsv(self, five_report_facts_ctl, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        mocker.patch.object(nark.reports.tsv_writer.TSVWriter, 'write_facts')
        controller = five_report_facts_ctl
        list_facts(controller, output_format='tsv')
        assert nark.reports.tsv_writer.TSVWriter.write_facts.called

    def test_ical(self, five_report_facts_ctl, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        mocker.patch.object(nark.reports.ical_writer.ICALWriter, 'write_facts')
        controller = five_report_facts_ctl
        list_facts(controller, output_format='ical')
        assert nark.reports.ical_writer.ICALWriter.write_facts.called

    def test_xml(self, five_report_facts_ctl, mocker):
        """Ensure passing 'xml' as format returns appropriate writer class."""
        mocker.patch.object(nark.reports.xml_writer.XMLWriter, 'write_facts')
        controller = five_report_facts_ctl
        list_facts(controller, output_format='xml')
        assert nark.reports.xml_writer.XMLWriter.write_facts.called

    def test_with_since(self, controller, mocker):
        """Make sure that passing a end date is passed to the fact gathering method."""
        # (lb): Not sure utility of this test. It was from hamster-lib, so I
        # probably refactored away any utility.
        mocker.patch.object(controller.facts, 'gather')
        since = fauxfactory.gen_datetime()
        # Get rid of fractions of a second.
        since = truncate_to_whole_seconds(since)
        list_facts(
            controller,
            output_format='csv',
            since=since.strftime('%Y-%m-%d %H:%M'),
        )
        args, kwargs = controller.facts.gather.call_args
        query_terms = args[0]
        assert query_terms.since == since

    def test_with_until(self, controller, mocker):
        """Make sure that passing a until date is passed to the fact gathering method."""
        mocker.patch.object(controller.facts, 'gather')
        until = fauxfactory.gen_datetime()
        # Get rid of fractions of a second.
        until = truncate_to_whole_seconds(until)
        list_facts(
            controller,
            output_format='csv',
            until=until.strftime('%Y-%m-%d %H:%M'),
        )
        args, kwargs = controller.facts.gather.call_args
        query_terms = args[0]
        assert query_terms.until == until

    def test_with_filename(self, five_report_facts_ctl, tmpdir, mocker):
        """Make sure that a valid format returns the appropriate writer class."""
        path = os.path.join(tmpdir.ensure_dir('export').strpath, 'export.csv')
        mocker.patch.object(nark.reports.csv_writer.CSVWriter, 'write_facts')
        controller = five_report_facts_ctl
        list_facts(controller, output_format='csv', output_path=path)
        assert nark.reports.csv_writer.CSVWriter.write_facts.called

