# This file exists within 'dob':
#
#   https://github.com/hotoffthehamster/dob
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

from collections import namedtuple
from collections.abc import Iterable
from operator import attrgetter

from gettext import gettext as _

from nark.backends.sqlalchemy.managers import query_sort_order_at_index
from nark.backends.sqlalchemy.managers.fact import FactManager
from nark.helpers.format_time import format_delta

from dob_bright.termio.ascii_table import generate_table

from ..facts_format.journal import output_time_journal

__all__ = (
    'generate_facts_table',
    'output_ascii_table',
    'report_table_columns',
)


def output_ascii_table(
    controller,
    results,
    query_terms,
    row_limit=0,
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    custom_columns=None,
    chop=False,
    table_type='friendly',
    spark_total=None,
    spark_width=None,
    spark_secs=None,
):
    for_journal = table_type == 'journal'

    table, headers, desc_col_idx = generate_facts_table(
        controller,
        results,
        query_terms=query_terms,
        row_limit=row_limit,
        show_usage=not hide_usage,
        show_duration=not hide_duration,
        show_description=not hide_description,
        custom_columns=custom_columns,
        for_journal=for_journal,
        spark_total=spark_total,
        spark_width=spark_width,
        spark_secs=spark_secs,
    )

    if for_journal:
        output_time_journal(
            table,
        )
    else:
        generate_table(
            table,
            headers,
            table_type,
            truncate=chop,
            trunccol=desc_col_idx,
        )


# ***

_ReportColumn = namedtuple('_ReportColumn', ('column', 'header', 'option'))

FACT_TABLE_HEADERS = {
    # Fact attributes.
    'key': _ReportColumn('key', _("Key"), True),
    'start': _ReportColumn('start', _("Start"), True),
    'end': _ReportColumn('end', _("End"), True),
    'activity': _ReportColumn('activity', _("Activity"), True),
    'category': _ReportColumn('category', _("Category"), True),
    'tags': _ReportColumn('tags', _("Tags"), True),
    'description': _ReportColumn('description', _("Description"), True),
    # Group-by aggregates. See: FactManager.RESULT_GRP_INDEX.
    'duration': _ReportColumn('duration', _("Duration"), True),
    # The journal format shows a sparkline.
    # MAYBE/2020-05-18: Add sparkline option to ASCII table formats.
    'sparkline': _ReportColumn('sparkline', _("Sparkline"), True),
    'group_count': _ReportColumn('group_count', _("Uses"), True),
    # MAYBE/2020-05-18: Format first_start and final_end per user --option.
    # - For now, ASCII table formatter is just str()'ifying.
    'first_start': _ReportColumn('first_start', _("First Start"), True),
    'final_end': _ReportColumn('final_end', _("Final End"), True),
    'activities': _ReportColumn('activities', _("Activities"), True),
    'actegories': _ReportColumn('actegories', _("Actegories"), True),
    'categories': _ReportColumn('categories', _("Categories"), True),
    # The actegory is used for the journal format.
    'actegory': _ReportColumn('actegory', _("Actegory"), True),
    # A singular 'tag' column happens when Act@Cat aggregated b/c group_tags.
    'tag': _ReportColumn('tag', _("Tag"), True),
    # More options for the journal format:
    'start_date': _ReportColumn('start_date', _("Start date"), True),
    'start_date_cmp': _ReportColumn('start_date_cmp', _("Startdate"), False),
    'start_time': _ReportColumn('start_time', _("Start time"), True),
    'end_date': _ReportColumn('end_date', _("End date"), True),
}


def report_table_columns():
    return [item.column for key, item in FACT_TABLE_HEADERS.items() if item.option]


def generate_facts_table(
    controller,
    results,
    query_terms,
    row_limit=0,
    # The user can pick some columns to hide/show:
    show_usage=True,
    show_duration=True,
    show_description=True,
    # Or the user could specify the columns they want:
    custom_columns=None,
    # Or this could be for a journal, in which case we decide:
    for_journal=False,
    spark_total=None,
    spark_width=None,
    spark_secs=None,
):
    """
    Prepares Facts for display in an ASCII table.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances, each representing a single Fact, or the summary of a
    group of Facts.
    """
    qt = query_terms

    columns = []
    repcols = {}
    sorting_columns = None

    if not custom_columns:
        include_usage = show_usage
        include_duration = show_duration
        include_description = show_description
    else:
        include_usage = 'group_count' in custom_columns
        include_duration = 'duration' in custom_columns
        include_description = 'description' in custom_columns

    i_cum_duration = FactManager.RESULT_GRP_INDEX['duration']
    i_group_count = FactManager.RESULT_GRP_INDEX['group_count']
    i_first_start = FactManager.RESULT_GRP_INDEX['first_start']
    i_final_end = FactManager.RESULT_GRP_INDEX['final_end']
    i_activities = FactManager.RESULT_GRP_INDEX['activities']
    i_actegories = FactManager.RESULT_GRP_INDEX['actegories']
    i_categories = FactManager.RESULT_GRP_INDEX['categories']
    i_date_col = FactManager.RESULT_GRP_INDEX['date_col']

    # A special index into the gross_totals lookup.
    # MAYBE/2020-05-18: Convert gross_totals to a class object...
    i_max_duration = i_final_end + 1

    resort_always = False
    # YOU: Uncomment to test re-sorting mechanism (in lieu of
    # crafting a custom `dob list` command that triggers the
    # code).
    #  resort_always = True

    def _generate_facts_table():
        test_result = results[0] if results else None
        headers, TableRow, sortref_cols = prepare_columns(test_result)

        gross_totals = initial_gross()

        table_rows = []
        n_row = 0
        for result in results:
            n_row += 1
            if row_limit and row_limit > 0 and n_row > row_limit:
                break

            fact_etc = prepare_fact_and_aggs_list(result)
            table_row = prepare_row(fact_etc)
            table_rows.append(table_row)

            update_gross(fact_etc, gross_totals)

        create_sparklines(table_rows, gross_totals)

        table = [TableRow(**table_row) for table_row in table_rows]
        last_chance_sort_results(table, TableRow, sortref_cols)

        table_row = produce_gross(gross_totals)
        if table_row is not None:
            empty_row = {key: '' for key in table_row.copy().keys()}
            table.append(TableRow(**empty_row))
            table.append(TableRow(**table_row))

        desc_col_idx = deduce_trunccol()

        return (table, headers, desc_col_idx)

    # ***

    def prepare_columns(test_result):
        columns[:], sortref_cols = assemble_columns(test_result)
        headers = [FACT_TABLE_HEADERS[column].header for column in columns]
        repcols.update({
            key: val for key, val in FACT_TABLE_HEADERS.items() if key in columns
        })
        TableRow = namedtuple('TableRow', columns)
        return headers, TableRow, sortref_cols

    # +++

    def assemble_columns(test_result):
        report_columns = assemble_columns_report(test_result)
        sortref_cols = extend_columns_sorting(report_columns)
        return report_columns, sortref_cols

    def assemble_columns_report(test_result):
        if custom_columns:
            return assemble_columns_report_custom()
        return assemble_columns_report_deduce(test_result)

    def assemble_columns_report_custom():
        custom_cols = assemble_columns_report_custom_build()
        return assemble_columns_report_custom_sanitize(custom_cols)

    def assemble_columns_report_custom_build():
        # Cull list of duplicates, retaining order.
        seen = set()
        seen_add = seen.add
        return [
            col for col in custom_columns
            if not (col in seen or seen_add(col))
        ]

    def assemble_columns_report_custom_sanitize(custom_cols):
        if qt.is_grouped:
            disallow = set([
                'key',
                'start',
                'end',
                'description',
            ])
            # MAYBE/2020-05-20: Should we disallow 'activity' if not group_activity?
            # - Disallow 'category' if not group_category.
            # - Disallow 'tags' if group_tags (and disallow 'tag' otherwise).
            # - What about 'activities', 'actegories', 'categories', 'actegory'?
        else:
            # Not is_grouped.
            disallow = set([
                'activities',
                'actegories',
                'categories',
                'actegory',
                'tag',
            ])
        return [col for col in custom_columns if col not in disallow]

    def assemble_columns_report_deduce(test_result):
        aggregate_cols = assemble_columns_sample_aggregate(test_result)
        if for_journal:
            return assemble_columns_for_journal(aggregate_cols)
        elif not qt.include_stats:
            return assemble_columns_single_fact()
        return assemble_columns_fact_and_aggs(aggregate_cols)

    def assemble_columns_sample_aggregate(test_result):
        if test_result and isinstance(test_result, Iterable):
            _fact, *aggregate_cols = test_result
        else:
            aggregate_cols = group_cols_shim(test_result)
        return aggregate_cols

    def extend_columns_sorting(report_columns):
        # reference_cols = set(sorting_columns).difference(set[report_columns])
        reference_cols = [col for col in sorting_columns if col not in report_columns]
        report_columns.extend(reference_cols)
        return (sorting_columns, reference_cols)

    # +++

    def assemble_columns_for_journal(aggregate_cols):
        # Start by deciding which columns to show first,
        # which depends on sorting and grouping.
        time_cols = []
        if qt.group_days:
            first_cols = ['start_date']
        else:
            sort_attr = attr_for_sort_col()
            first_cols = journal_first_columns(aggregate_cols, sort_attr)
            if not first_cols:
                # first_cols = ['start_date', 'start_time']
                first_cols = ['end_date', 'start_time']
            elif qt.is_grouped:
                # FIXME: make date format Fri Jun 29  9:30am but let user change...
                time_cols = ['first_start', 'final_end']
            else:
                time_cols = ['start', 'end']

        # Gather the Fact attribute columns to display, which depends on
        # which aggregate columns were used in the query. We also add the
        # separator, '@', because the journal view does not use column
        # headers, and without, the user would have no context, and would
        # not know their activities from their categories.
        meta_cols = assemble_columns_fact_and_aggs_meta(aggregate_cols)
        # Remove meta_cols that may have been promoted to first positions.
        meta_cols = [col for col in meta_cols if col not in first_cols]

        # Default order (unless user overrides, in which case this function
        # is not called), is to show some main identifier column(s) (as
        # determined by journal_first_columns), that some statistics (which
        # we'll add now), followed by the time columns (if not already shown)
        # and then the remaining attribute columns (not already shown).
        _columns = []
        _columns.extend(first_cols)
        _columns.append('duration')
        _columns.append('sparkline')
        _columns.extend(time_cols)
        _columns.extend(meta_cols)
        if not qt.group_days:
            _columns.append('start_date')
        else:
            _columns.append('start_date_cmp')

        return _columns

    def attr_for_sort_col():
        # --sort [name|activity|category|tag|fact|start|usage|time|day]
        sort_col = qt.sort_cols[0] if qt.sort_cols else ''
        if sort_col in ('activity', 'category', 'tag'):
            return sort_col
        return ''

    def journal_first_columns(aggregate_cols, sort_attr):
        # The special value used is 0, but cannot hurt to check None, too.
        if aggregate_cols[i_activities] not in [0, None]:
            # group_category (and maybe group_tags, too).
            if sort_attr == 'category':
                return ['category']
            elif sort_attr == 'activity':
                return ['activities']
            elif sort_attr == 'tag':
                return ['tags']
        elif aggregate_cols[i_actegories] not in [0, None]:
            # group_tags (but neither group_category or group_activity).
            if sort_attr == 'tag':
                if qt.group_days:
                    return ['tags']
                else:
                    return ['tag']
            elif sort_attr == 'activity' or sort_attr == 'category':
                return ['actegories']
        elif aggregate_cols[i_categories] not in [0, None]:
            # group_activity (and maybe group_tags, too).
            if sort_attr == 'activity':
                return ['activity']
            elif sort_attr == 'category':
                return ['categories']
            elif sort_attr == 'tag':
                return ['tags']
        elif qt.group_days:
            return None
        elif qt.is_grouped:
            # group_activity and group_category.
            return ['actegory']
        # else, nothing grouped, and not sorting on Fact attribute.
        # - So. --sort either not specified, or: [name|fact|start|usage|time]
        return None

    # +++

    def assemble_columns_single_fact():
        _columns = [
            'key',
            'start',
            'end',
            'activity',
            'category',
            'tags',
        ]
        if include_description:
            _columns.append('description')
        if include_duration:
            _columns.append('duration')
        return _columns

    # +++

    def assemble_columns_fact_and_aggs(aggregate_cols):
        _columns = []
        _columns.extend(assemble_columns_fact_and_aggs_meta(aggregate_cols))
        assemble_columns_fact_and_aggs_duration(aggregate_cols, _columns)
        assemble_columns_fact_and_aggs_usage(aggregate_cols, _columns)
        return _columns

    def assemble_columns_fact_and_aggs_meta(aggregate_cols):
        meta_cols = []
        # The special value used is 0, but cannot hurt to check None, too.
        if aggregate_cols[i_activities] not in [0, None]:
            # group_category (and maybe group_tags, too).
            meta_cols.append('category')
            meta_cols.append('activities')
            meta_cols.append('tags')
        elif aggregate_cols[i_actegories] not in [0, None]:
            # group_tags (but neither group_category or group_activity).
            if qt.group_days:
                meta_cols.append('tags')
            else:
                meta_cols.append('tag')
            meta_cols.append('actegories')
        elif aggregate_cols[i_categories] not in [0, None]:
            # group_activity (and maybe group_tags, too).
            meta_cols.append('activity')
            meta_cols.append('categories')
            meta_cols.append('tags')
        else:
            # group_activity and group_category, or nothing grouped.
            if not for_journal:
                meta_cols.append('activity')
                meta_cols.append('category')
            else:
                meta_cols.append('actegory')
            meta_cols.append('tags')
        return meta_cols

    def assemble_columns_fact_and_aggs_duration(aggregate_cols, _columns):
        if not include_duration:
            return

        _columns.append('duration')

    def assemble_columns_fact_and_aggs_usage(aggregate_cols, _columns):
        if not include_usage:
            return

        _columns.append('group_count')
        _columns.append('first_start')
        _columns.append('final_end')

    # +++

    def group_cols_shim(fact):
        cols_shim = [None] * len(FactManager.RESULT_GRP_INDEX)
        # Because julianday, expects days. MAGIC_NUMBER: 86400 secs/day.
        cols_shim[i_cum_duration] = fact.delta().total_seconds() / 86400.0
        cols_shim[i_group_count] = 1
        cols_shim[i_first_start] = fact.start
        cols_shim[i_final_end] = fact.end
        # 0 is what get_all uses in place of group_concat (which emits a string).
        cols_shim[i_activities] = 0
        cols_shim[i_actegories] = 0
        cols_shim[i_categories] = 0
        cols_shim[i_date_col] = None
        return cols_shim

    # ***

    def prepare_fact_and_aggs_list(result):
        # Get ready to unpack the Fact and the aggregate columns by first
        # ensuring that the result is unpackable (but creating the aggregate
        # columns if necessary).
        # - We could deduce the structure of the result by checking our bools:
        #     if not is_grouped and not include_usage:
        #   but checking if an iterable seems more robust/readable.
        if isinstance(result, Iterable):
            # Already packed.
            return result
        # The result is a simple Fact. Create the equivalent aggregate columns.
        aggregate_cols = group_cols_shim(result)
        return result, *aggregate_cols

    def prepare_row(fact_etc):
        # Each result is a tuple: First the Fact, and then the
        # aggregate columns (see FactManager.RESULT_GRP_INDEX).
        (
            fact,
            duration,
            group_count,
            first_start,
            final_end,
            activities,
            actegories,
            categories,
            date_col,
        ) = fact_etc

        if not final_end:
            final_end = controller.store.now

        table_row = {}

        prepare_key(table_row, fact)

        prepare_starts_and_end(
            table_row, fact, first_start, final_end, date_col,
        )
        prepare_activity_and_category(
            table_row, fact, activities, actegories, categories,
        )
        prepare_duration(table_row, fact, duration)
        prepare_group_count(table_row, group_count)
        prepare_first_start(table_row, first_start)
        prepare_final_end(table_row, final_end)
        prepare_description(table_row, fact)

        row_slice = unprepare_unmentioned_columns(table_row)

        return row_slice

    # ***

    def prepare_key(table_row, fact):
        if 'key' not in repcols:
            return

        table_row['key'] = fact.pk

    # +++

    def prepare_starts_and_end(table_row, fact, first_start, final_end, date_col):
        prepare_start_date(table_row, fact, first_start)
        prepare_start_date_cmp(table_row, fact, first_start, date_col)
        prepare_start_time(table_row, fact, first_start)
        prepare_end_date(table_row, fact, final_end)
        prepare_start(table_row, fact)
        prepare_end(table_row, fact)

    def prepare_start_date(table_row, fact, first_start):
        if 'start_date' not in repcols:
            return

        # MAYBE/2020-05-18: Make this and other strftime formats --option'able.
        start_date = first_start.strftime('%a %b %d') if first_start else ''
        table_row['start_date'] = start_date

    def prepare_start_date_cmp(table_row, fact, first_start, date_col):
        if 'start_date_cmp' not in repcols:
            return

        # The SQLite date(col) produces, e.g., '2020-05-14'.
        if date_col:
            start_date_cmp = date_col
        else:
            start_date_cmp = first_start.strftime('%Y-%m-%d') if first_start else ''
        table_row['start_date_cmp'] = start_date_cmp

    def prepare_start_time(table_row, fact, first_start):
        if 'start_time' not in repcols:
            return

        start_time = first_start.strftime('%H:%M') if first_start else ''
        table_row['start_time'] = start_time

    def prepare_end_date(table_row, fact, final_end):
        if 'end_date' not in repcols:
            return

        end_date = final_end.strftime('%a %b %d') if final_end else ''
        table_row['end_date'] = end_date

    def prepare_start(table_row, fact):
        if 'start' not in repcols:
            return

        if fact.start:
            # MAYBE/2020-05-18: Make the datetime format an --option.
            fact_start = fact.start.strftime('%Y-%m-%d %H:%M')
        else:
            fact_start = _('<genesis>')
            controller.client_logger.warn('Fact missing start: {}').format(fact)
        table_row['start'] = fact_start

    def prepare_end(table_row, fact):
        if 'end' not in repcols:
            return

        if fact.end:
            fact_end = fact.end.strftime('%Y-%m-%d %H:%M')
        else:
            # FIXME: This is just the start of supporting open ended Fact in db.
            fact_end = _('<active>')
            # Replace None with 'now', so that fact.delta() returns something
            # (that is, if we don't use the 'duration' from the results, which was
            # calculated by the SQL query (using the computed 'endornow' column)).
            fact.end = controller.now
        table_row['end'] = fact_end

    # +++

    def prepare_activity_and_category(
        table_row, fact, activities, actegories, categories,
    ):
        # The special value used is 0, but cannot hurt to check None, too.
        if activities not in [None, 0]:
            # Grouped by category (and possibly tags, too).
            prepare_category(table_row, fact)
            prepare_activities(table_row, activities)
            prepare_tagnames(table_row, fact)
        elif actegories not in [None, 0]:
            # Group by tags but not activity or category.
            prepare_actegories(table_row, actegories)
            if qt.group_days:
                prepare_tagnames(table_row, fact)
            else:
                # Else, group_tags, so one each.
                prepare_tagname(table_row, fact)
        elif categories not in [None, 0]:
            # Group by activity name (and possibly tags, too).
            prepare_activity(table_row, fact)
            prepare_categories(table_row, categories)
            prepare_tagnames(table_row, fact)
        else:
            # Group by activity ID and category ID, or no grouping.
            if not for_journal:
                prepare_activity(table_row, fact)
                prepare_category(table_row, fact)
            else:
                prepare_actegory(table_row, fact)
            prepare_tagnames(table_row, fact)

    def prepare_activity(table_row, fact):
        if 'activity' not in repcols:
            return

        table_row['activity'] = fact.activity_name + actcatsep()

    def prepare_activities(table_row, activities, sep=_(', ')):
        if 'activities' not in repcols:
            return

        table_row['activities'] = sep.join(
            [activity + actcatsep() for activity in sorted(activities)]
        )

    def prepare_actegories(table_row, actegories, sep=_(', ')):
        if 'actegories' not in repcols:
            return

        table_row['actegories'] = sep.join(sorted(actegories))

    def prepare_categories(table_row, categories, sep=_(', ')):
        if 'categories' not in repcols:
            return

        table_row['categories'] = sep.join(
            [actcatsep() + category for category in sorted(categories)]
        )

    def prepare_category(table_row, fact):
        if 'category' not in repcols:
            return

        table_row['category'] = actcatsep() + fact.category_name

    def prepare_actegory(table_row, fact):
        if 'actegory' not in repcols:
            return

        table_row['actegory'] = fact.oid_actegory()

    # MAYBE/2020-05-18: Make the '@' symbol configable.
    def actcatsep(sep=_('@')):
        if for_journal:
            return sep
        return ''

    # +++

    def prepare_tagnames(table_row, fact):
        if 'tags' not in repcols:
            return

        table_row['tags'] = assemble_tags(fact.tags)

    def prepare_tagname(table_row, fact):
        if 'tag' not in repcols:
            return

        controller.affirm(len(fact.tags) <= 1)
        table_row['tag'] = assemble_tags(fact.tags)

    def assemble_tags(fact_tags):
        if fact_tags:
            # FIXME/2020-05-18: Use '#' symbol specified in config.
            tags = ' '.join(sorted(['#' + x.name for x in fact_tags]))
        else:
            tags = ''
        return tags

    # +++

    def prepare_duration(table_row, fact, duration):
        if not include_duration:
            return

        # Note that the 'duration' will be similar to fact.format_delta()
        # unless is_grouped, in which case 'duration' is an aggregate value.
        # But in either case, the 'duration' in the results is expressed in days.
        if 'sparkline' not in columns:
            # Finalize the duration as a string value.
            duration = format_fact_or_query_duration(fact, duration)
        # else, we'll prepare a sparkline later, so keep the durations value
        # (in secs.), until we post-process it.
        elif not duration:
            duration = fact.delta().total_seconds()
        else:
            duration = convert_duration_days_to_secs(duration)
        table_row['duration'] = duration

    def format_fact_or_query_duration(fact, duration):
        if not duration:
            # MAYBE/2020-05-18: Use format_duration_secs() instead, to be
            # consistent.
            #  fmt_duration = fact.format_delta(style='')
            duration_secs = fact.delta().total_seconds()
        else:
            #  fmt_duration = format_duration_days(duration)
            duration_secs = convert_duration_days_to_secs(duration)
        fmt_duration = format_duration_secs(duration_secs)
        return fmt_duration

    # - MAGIC_NUMBER: 86400 seconds/day, to convert between timedelta
    #                 (seconds) and SQLite julianday computation (days).
    SECONDS_IN_DAY = 86400.0

    def convert_duration_days_to_secs(duration):
        # - The duration was computed by julianday math, so it's in days,
        #   and format_delta expects seconds, so convert to the latter.
        durasecs = duration * SECONDS_IN_DAY
        return durasecs

    def format_duration_days(duration):
        durasecs = convert_duration_days_to_secs(duration)
        fmt_duration = format_duration_secs(durasecs)
        return fmt_duration

    def format_duration_secs(durasecs):
        # Use pedantic_timedelta to format the duration.
        style = ''
        # MAGIC_NUMBERS: Specify the formatted field width and precision.
        # - Use a field width so the column values align --
        #   a field_width of 4 will align most values, e.g.,
        #        aligned:        not aligned:
        #       12.5 hours       12.5 hours
        #        1.0 mins.       1.0 mins.
        # - Also set precision=1, as the default, 2, is more precision
        #   than the user needs.
        #   - I also think that looking at, say, "7.02 minutes" is more
        #     complicated/distracting than seeing "7.0 minutes". My brain
        #     pauses longer to digest the hundredths place, but the extra
        #     information is of no value to me.
        fmt_duration = format_delta(
            durasecs, style=style, field_width=4, precision=1,
        )
        return fmt_duration

    # +++

    def create_sparklines(table_rows, gross_totals):
        if 'sparkline' not in columns:
            return

        # REMINDER: These values are in days.
        cum_duration = convert_duration_days_to_secs(gross_totals[i_cum_duration])
        max_duration = convert_duration_days_to_secs(gross_totals[i_max_duration])

        if not spark_total or spark_total == 'max':
            spark_max_value = max_duration
        elif spark_total == 'net':
            spark_max_value = cum_duration
        else:
            # The user directly specified some number of seconds.
            # - This sets a custom max value reference, e.g., you could
            #   set the full width of a sparkline to represent 8 hours:
            #       spark_max_value = 8 * 60 * 60  # 8 hours.
            #   Or from the CLI:
            #       dob list ... --spark-total '8 * 60 * 60'
            # - Note that if this is less than max_duration, some sparklines
            #   will run over their allotted column width.
            spark_max_value = spark_total

        # MAGIC_NUMBER: Prefer --spark-width, or default to a 12-character
        # width, just to do something so the width is not nothing.
        spark_chunk_width = spark_width or 12

        # User can specify --spark-secs, or we'll calculate from
        # the previous two values: this is the seconds represented
        # by one █ block, i.e., the full block time divided by the
        # total number of blocks being used (or at least the number
        # of blocks it would take to fill the specified field width).
        # - HINT: This option eval-aware, e.g., 1 hour: --spark-secs '60 * 60'.
        spark_chunk_secs = spark_secs or (spark_max_value / spark_chunk_width)

        def prepare_sparkline(table_row):
            # We stashed the duration as seconds.
            dur_seconds = table_row['duration']
            sparkline = spark_up(dur_seconds, spark_chunk_secs)
            table_row['sparkline'] = sparkline

            # We've used the seconds value, so now we can format the duration.
            table_row['duration'] = format_duration_secs(dur_seconds)

        def spark_up(dur_seconds, spark_chunk_secs):
            # Thanks to:
            #   https://alexwlchan.net/2018/05/ascii-bar-charts/
            # MAGIC_NUMBER: The ASCII block elements come in 8 widths.
            #   https://en.wikipedia.org/wiki/Block_Elements
            n_chunks, remainder = divmod(dur_seconds, spark_chunk_secs)
            n_eighths = int(8 * (remainder / spark_chunk_secs))
            # Start with the full-width block elements.
            sparkline = '█' * int(n_chunks)
            # Add the fractional block element. Note that the Unicode
            # code points for block elements are decreasingly ordered,
            # (8/8), (7/8), (6/8), etc., so subtract the number of eighths.
            if n_eighths > 0:
                # MAGIC_NUMBER: The Block Element code points are sequential,
                #   and there are 9 of them (1 full width + 8 eighths).
                sparkline += chr(ord('█') + (8 - n_eighths))
            # If the sparkline is empty, show at least a little something.
            # - Add a left one-eighth block.
            sparkline = sparkline or '▏'
            # Pad the result.
            sparkline = '{:{}s}'.format(sparkline, spark_chunk_width)
            return sparkline

        # +++

        for table_row in table_rows:
            prepare_sparkline(table_row)

    # +++

    def prepare_group_count(table_row, group_count):
        if 'group_count' not in repcols:
            return

        table_row['group_count'] = group_count

    def prepare_first_start(table_row, first_start):
        if 'first_start' not in repcols:
            return

        table_row['first_start'] = first_start

    def prepare_final_end(table_row, final_end):
        if 'final_end' not in repcols:
            return

        table_row['final_end'] = final_end

    # +++

    def prepare_description(table_row, fact):
        if 'description' not in repcols:
            return

        table_row['description'] = fact.description or ''

    # ***

    # MAYBE/2020-05-20: This function can probably be removed.
    # (lb): I added `X not in repcols` checks to all the `table_row[Y] =` functions.
    # So I'd guess the table_row is has the correct attrs, and none superfluous.
    def unprepare_unmentioned_columns(table_row):
        if custom_columns is None:
            return table_row

        # Rebuild the table row, but exclude excluded columns.
        # (lb): We could add `'column' not in columns` to every prepare_*
        # function, but that'd be noisy. Seems better to rebuild the dict.
        row_slice = {
            key: val for key, val in table_row.items() if key in columns
        }

        # Add any columns the user specified that are missing, e.g.,
        # if the user added, say, 'description' to an aggregate query.
        # (This is us being nice, so we don't stack trace just because
        # the user specified a "weird" combination of CLI options.)
        missing = [key for key in columns if key not in row_slice]
        for key in missing:
            row_slice[key] = ''

        return row_slice

    # ***

    def initial_gross():
        # MAGIC_ARRAY: Create aggregate values of all results.
        # These are the indices of this results aggregate:
        #   0: Durations summation.
        #   1: Group count count.
        #   2: First first_start.
        #   3: Final final_end.
        #   Skip: Activities, Actegories, Categories.
        # - See: FactManager.RESULT_GRP_INDEX.
        # - Also add an additional member not in RESULT_GRP_INDEX:
        #   4: Maximum duration.
        gross_totals = [0, 0, None, None, 0]
        return gross_totals

    # +++

    def update_gross(fact_etc, gross_totals):
        _fact, *cols = fact_etc
        duration = cols[i_cum_duration]
        group_count = cols[i_group_count]
        first_start = cols[i_first_start]
        final_end = cols[i_final_end] or controller.store.now
        update_gross_values(
            gross_totals, duration, group_count, first_start, final_end,
        )

    def update_gross_values(
        gross_totals, duration, group_count, first_start, final_end,
    ):
        gross_totals[i_cum_duration] += duration
        gross_totals[i_max_duration] = max(gross_totals[i_max_duration], duration)

        gross_totals[i_group_count] += group_count

        if gross_totals[i_first_start] is None:
            gross_totals[i_first_start] = first_start
        else:
            gross_totals[i_first_start] = min(
                gross_totals[i_first_start], first_start,
            )

        if gross_totals[i_final_end] is None:
            gross_totals[i_final_end] = final_end
        else:
            gross_totals[i_final_end] = max(
                gross_totals[i_final_end], final_end,
            )

    # +++

    def produce_gross(gross_totals):
        if gross_totals is None:
            return None

        # Start with defaults for each column.
        # - We could show empty cells for most of the columns:
        #     table_row = {name: '' for name in columns}
        #   But it seems more helpful to label the row as containing totals.
        #   - Without making this more complicated and poking around
        #     'columns' for an appropriate column cell to label, let's
        #     just label all the values in the row 'TOTAL', and then
        #     overwrite some of those cell values from gross_totals.
        #   - MAYBE/2020-05-18: Improve the look of the final column.
        #     I.e., don't just blindly write 'TOTAL' in each cell,
        #     but figure out the first non-gross_totals column (from
        #     'columns') and write 'TOTAL' to just that one cell.
        table_row = {name: _('TOTAL') for name in columns}

        # Now set values for appropriate columns.
        produce_gross_duration(gross_totals, table_row)
        produce_gross_group_count(gross_totals, table_row)
        produce_gross_first_start(gross_totals, table_row)
        produce_gross_final_end(gross_totals, table_row)

        # Remove columns that may be omitted.
        row_slice = unprepare_unmentioned_columns(table_row)

        return row_slice

    def produce_gross_duration(gross_totals, table_row):
        if 'duration' not in repcols:
            return

        # The SQLite aggregate result is in (julian)days, but the
        # timedelta is specified in seconds, so convert to the latter.
        fmt_duration = format_duration_days(gross_totals[i_cum_duration])
        table_row['duration'] = fmt_duration
        return fmt_duration

    def produce_gross_group_count(gross_totals, table_row):
        if 'group_count' not in repcols:
            return

        table_row['group_count'] = gross_totals[i_group_count]

    def produce_gross_first_start(gross_totals, table_row):
        if 'first_start' not in repcols:
            return

        table_row['first_start'] = gross_totals[i_first_start]

    def produce_gross_final_end(gross_totals, table_row):
        if 'final_end' not in repcols:
            return

        table_row['final_end'] = gross_totals[i_final_end]

    # ***

    def last_chance_sort_results(table, row_cls, sortref_cols):
        if not table:
            return

        # Check each sort_col to see if we care, i.e. if get_all was not
        # able to sort on that value in the SQL statement. First check
        # lazily, that is, only indicate which sort cols are ones that
        # did not work in the SQL statement.
        needs_sort = any([
            sort_attrs_for_col(row_cls, sort_col, lazy=True)
            for sort_col in qt.sort_cols
        ])

        if not needs_sort and not resort_always:
            controller.client_logger.warn('Skipping re-sort.')
            return
        controller.client_logger.warn('Post Processing: Re-SORTing.')

        expect_cols = sorting_columns.copy()
        for idx, sort_col in reversed(list(enumerate(qt.sort_cols))):
            sort_order = query_sort_order_at_index(qt.sort_orders, idx)
            sort_results_sort_col(table, row_cls, sort_col, sort_order, expect_cols)

    def sort_results_sort_col(table, row_cls, sort_col, sort_order, expect_cols):
        # Because we are redoing the whole sort, use lazy=False.
        sort_attrs = sort_attrs_for_col(row_cls, sort_col, lazy=False)
        verify_available_sort_cols_match_anticipated(sort_attrs, expect_cols)
        sort_attrs.reverse()
        for sort_attr in sort_attrs:
            reverse = sort_order == 'desc'
            table.sort(key=attrgetter(sort_attr), reverse=reverse)

        return table

    def sort_attrs_for_col(row_cls, sort_col, lazy):
        # MAYBE/2020-05-20: Replace this fnc. with sort_col_actual.
        # - (lb): I wrote sort_col_actual after this one... sort_col_actual
        #   is more predictive (it forecasts the columns, from the SQL query
        #   or that we'll calculate during post-processing, that will be
        #   needed to sort); whereas this function is more reactive (it
        #   looks at the actual columns after post-processing and uses
        #   what's available). / Or maybe the 2 fcns. are nice to have,
        #   1 to tell us what columns to maintain during post processing,
        #   and then this fcn. to not accidentally sort on a missing column.
        # - For now, I verify the two sets of columns are equivalent;
        #   see: verify_available_sort_cols_match_anticipated.
        sort_attrs = []

        if sort_col == 'activity':
            if hasattr(row_cls, 'activities'):
                # group_category on its own; SQL could not sort.
                sort_attrs = ['activities']
            elif not lazy:
                # Both of these cases can be sorted by SQL (hence not lazy).
                if hasattr(row_cls, 'actegory'):
                    # group_activity and group_category.
                    sort_attrs = ['actegory']
                elif hasattr(row_cls, 'activity'):
                    sort_attrs = ['activity']
                else:
                    controller.client_logger.warn(
                        "Did not identify sort column for --sort activity!"
                    )

        elif sort_col == 'category':
            if hasattr(row_cls, 'categories'):
                sort_attrs = ['categories']
            # else, if hasattr(row_cls, 'actegory'), category information
            # is missing. We could make a special case in the get_all
            # query, but doesn't seem like a big priority to handle.
            elif not lazy:
                if hasattr(row_cls, 'category'):
                    # FIXME/2020-05-20: This a thing?
                    sort_attrs = ['category']
                else:
                    controller.client_logger.warn(
                        "Did not identify sort column for --sort category!"
                    )

        elif sort_col == 'tag':
            if hasattr(row_cls, 'tag'):
                sort_attrs = ['tag']
            elif hasattr(row_cls, 'tags'):
                sort_attrs = ['tags']
            # elif not lazy:
                # FIXME/2020-05-20 06:03: What path is this??
                # sort_attrs = '???'
                # In get_all, it sorts on Tag.name itself.
            else:
                controller.client_logger.warn(
                    "Did not identify sort column for --sort tag!"
                )

        elif not lazy:
            # We could verify the return column exists, e.g., check
            # `hasattr(row_cls, 'foo')`, but the sort will just fail.
            # Should be a programming error, anyway, the code checks
            # the sort columns before processing results, and ensures
            # the necessary sort columns are ready for us here.
            if sort_col == 'start':
                if not qt.is_grouped:
                    sort_attrs = ['start', 'end', 'key']
                else:
                    sort_attrs = ['first_start', 'final_end']
            elif sort_col == 'time':
                sort_attrs = ['duration']
            elif sort_col == 'day':
                # FIXME/2020-05-20: Should we auto-add start_date_cmp sort option when
                #   --group-days? Or should we require user to specify `-o days`?
                #   Another option: `dob journal` command with sort_cols default, etc.
                sort_attrs = ['start_date_cmp']
            elif sort_col == 'usage':
                sort_attrs = ['group_count']
            elif sort_col == 'name':
                sort_attrs = ['description']
            elif sort_col == 'fact':
                sort_attrs = ['key']
            else:
                # If this fires, you probably added a --sort choice that you did
                # not wire herein.
                controller.client_logger.warn(
                    "Did not identify sort column for --sort {}!".format(sort_col)
                )

        return sort_attrs

    def verify_available_sort_cols_match_anticipated(sort_attrs, expect_cols):
        # NOTE: (lb): This is just a verification check, because I coded three
        #       very similar sort_cols processors:
        #           nark.backends.sqlalchemy.managers.fact.FactManager.query_order_by_aggregate
        #           dob.facts_format.tabular.sort_col_actual
        #           dob.facts_format.tabular.sort_attrs_for_col
        #       It just happened!
        # Before processing results, we called sort_on_cols_later() and
        # determined the sort cols based on sort_cols and the group_* state.
        # After processing results, we called sort_attrs_for_col to see what
        # columns were actually populated that we can sort on.
        # - The two should match, and if they don't, log a complaint.
        subexpect = expect_cols[-len(sort_attrs):]
        if subexpect != sort_attrs:
            controller.client_logger.warn(
                "Sort discrepency: sort_attrs: {} / expect_cols: {} (subexpect: {})"
                .format(sort_attrs, expect_cols, subexpect)
            )
            controller.affirm(False)
        else:
            # Remove the trailing, verified items from the expecting list.
            expect_cols[:] = expect_cols[:-len(sort_attrs)]

    # ***

    def sort_on_cols_later():
        actual_cols = []
        must_sort_later = False
        for sort_col in qt.sort_cols or []:
            target_cols, must_later = sort_col_actual(sort_col)
            actual_cols.extend(target_cols)
            must_sort_later = must_sort_later or must_later
        if not must_sort_later and not resort_always:
            actual_cols = []
        return actual_cols

    # Ref: nark.FactManager.query_order_by_sort_col.
    def sort_col_actual(sort_col):
        must_sort_later = False

        if sort_col == 'start' or not sort_col:
            if not qt.is_grouped:
                sort_attrs = ['start', 'end', 'key']
            else:
                sort_attrs = ['first_start', 'final_end']
        elif sort_col == 'time':
            sort_attrs = ['duration']
        elif sort_col == 'day':
            sort_attrs = ['start_date_cmp']
        elif sort_col == 'activity':
            if not qt.is_grouped or (qt.group_activity and qt.group_category):
                if not for_journal:
                    sort_attrs = ['activity']
                else:
                    sort_attrs = ['actegory']
            elif qt.group_activity:
                sort_attrs = ['activity']
            elif qt.group_tags or qt.group_days:
                must_sort_later = True
                sort_attrs = ['actegories']
            else:
                # group_category (by PK).
                must_sort_later = True
                sort_attrs = ['activities']
        elif sort_col == 'category':
            if not qt.is_grouped or (qt.group_activity and qt.group_category):
                if not for_journal:
                    sort_attrs = ['category']
                else:
                    # The journal generally use just actegory,
                    #   sort_attrs = ['actegory']
                    # but user did request sorting by category.
                    sort_attrs = ['category']
            elif qt.group_category:
                sort_attrs = ['category']
            elif qt.group_tags or qt.group_days:
                must_sort_later = True
                sort_attrs = ['actegories']
            else:
                # group_activity (by name, not PK).
                must_sort_later = True
                sort_attrs = ['categories']
        elif sort_col == 'tag':
            if not qt.is_grouped or not group_tag:
                sort_attrs = ['tags']
            else:
                sort_attrs = ['tag']
        elif sort_col == 'usage':
            sort_attrs = ['group_count']
        elif sort_col == 'name':
            sort_attrs = ['description']
        elif sort_col == 'fact':
            sort_attrs = ['key']
        else:
            controller.client_logger.warn("Unknown sort_col: {}".format(sort_col))

        # Return True to have this module's sort_results_sort_col sort,
        # regardless of what we this the SQL query accomplished. E.g,
        # uncomment this to test re-sorting results:
        #  must_sort_later = True
        must_sort_later = must_sort_later or resort_always

        return sort_attrs, must_sort_later

    # ***

    def deduce_trunccol():
        # This is very inexact psyence. (We could maybe expose this as a CLI
        # option.) Figure out which column is appropriate to truncate.
        # - (lb): Back in 2018 when I first wrote this, the 'description'
        #   seemed like the obvious column. But it's no longer always there.
        #   And also, now you can group-by columns, which can make for a
        #   very long actegories column. Even tags might be a candidate.
        for candidate in [
            'description',
            'actegories',
            'activities',
            'categories',
            'tags',
        ]:
            try:
                return columns.index(candidate)
            except ValueError:
                pass
        # Give up. No column identified.
        return None

    # ***

    # Check each sort_col to see if we care, i.e. if get_all was not
    # able to sort on that value in the SQL statement. First check
    # lazily, that is, only indicate which sort cols are ones that
    # did not work in the SQL statement.
    # ((lb): This is sorta a hack of functional programming... setting
    #  down here after sort_on_cols_later(), even though most of the
    #  function-scope variable are way up top. It's lines like these
    #  I realize perhaps I should've made this a class!)
    sorting_columns = sort_on_cols_later()

    return _generate_facts_table()

