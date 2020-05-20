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

from gettext import gettext as _

from nark.backends.sqlalchemy.managers.fact import FactManager
from nark.helpers.format_time import format_delta

from dob_bright.termio.ascii_table import generate_table


__all__ = (
    'generate_facts_table',
    'output_ascii_table',
)


def output_ascii_table(
    controller,
    results,
    row_limit,
    is_grouped,
    includes_extras,
    hide_usage=False,
    hide_duration=False,
    hide_description=False,
    custom_columns=None,
    chop=False,
    table_type='friendly',
    sort_cols=None,
    sort_orders=None,
    group_days=False,
):
    table, headers, desc_col_idx = generate_facts_table(
        controller,
        results,
        row_limit,
        is_grouped,
        includes_extras,
        show_usage=not hide_usage,
        show_duration=not hide_duration,
        show_description=not hide_description,
        custom_columns=custom_columns,
        group_days=group_days,
    )

    generate_table(
        table,
        headers,
        table_type,
        truncate=chop,
        trunccol=desc_col_idx,
    )


# ***

FACT_TABLE_HEADERS = {
    # Fact attributes.
    'key': _("Key"),
    'start': _("Start"),
    'end': _("End"),
    'activity': _("Activity"),
    'category': _("Category"),
    'tags': _("Tags"),
    'description': _("Description"),
    # Group-by aggregates. See: FactManager.RESULT_GRP_INDEX.
    'duration': _("Duration"),
    'group_count': _("Uses"),
    'first_start': _("First Start"),
    'final_end': _("Final End"),
    'activities': _("Activities"),
    'actegories': _("Actegories"),
    'categories': _("Categories"),
    # Use singular column header when Act@Cat aggregated b/c group_tags.
    'tag': _("Tag"),
}


def generate_facts_table(
    controller,
    results,
    row_limit,
    is_grouped,
    includes_extras,
    # The user can pick some columns to hide/show:
    show_usage=True,
    show_duration=True,
    show_description=True,
    # Or the user could specify the columns they want:
    custom_columns=None,
    group_days=False,
):
    """
    Prepares Facts for display in an ASCII table.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances, each representing a single Fact, or the summary of a
    group of Facts.
    """
    columns = []

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

    def _generate_facts_table():
        test_result = results[0] if results else None
        headers, TableRow = prepare_columns(test_result)

        gross_totals = initial_gross()

        table = []
        n_row = 0
        for result in results:
            n_row += 1
            if row_limit and row_limit > 0 and n_row > row_limit:
                break

            fact_etc = prepare_fact_and_aggs_list(result)
            table_row = prepare_row(fact_etc)
            table.append(TableRow(**table_row))

            update_gross(fact_etc, gross_totals)

        table_row = produce_gross(gross_totals)
        if table_row is not None:
            empty_row = {key: '' for key in table_row.copy().keys()}
            table.append(TableRow(**empty_row))
            table.append(TableRow(**table_row))

        desc_col_idx = deduce_trunccol()

        return (table, headers, desc_col_idx)

    # ***

    def prepare_columns(test_result):
        columns[:] = assemble_columns(test_result)
        headers = [FACT_TABLE_HEADERS[column] for column in columns]
        TableRow = namedtuple('TableRow', columns)
        return headers, TableRow

    # +++

    def assemble_columns(test_result):
        aggregate_cols = assemble_columns_sample_aggregate(test_result)

        if custom_columns:
            # Cull list of duplicates, retaining order.
            seen = set()
            seen_add = seen.add
            return [
                col for col in custom_columns
                if not (col in seen or seen_add(col))
            ]
        elif not includes_extras:
            return assemble_columns_single_fact()
        return assemble_columns_fact_and_aggs(aggregate_cols)

    def assemble_columns_sample_aggregate(test_result):
        if test_result and isinstance(test_result, Iterable):
            _fact, *aggregate_cols = test_result
        else:
            aggregate_cols = group_cols_shim(test_result)
        return aggregate_cols

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
            if group_days:
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
        cols_shim[i_date_col] = None  # Query sets None if not group_days.
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

    def prepare_row(fact_etc, row_cls):
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

        prepare_start(table_row, fact)
        prepare_end(table_row, fact)
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
        if is_grouped:
            return

        table_row['key'] = fact.pk

    # +++

    def prepare_start(table_row, fact):
        if is_grouped:
            return

        if fact.start:
            fact_start = fact.start.strftime('%Y-%m-%d %H:%M')
        else:
            fact_start = _('<genesis>')
            controller.client_logger.warning(_('Fact missing start: {}').format(fact))
        table_row['start'] = fact_start

    def prepare_end(table_row, fact):
        if is_grouped:
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
            if group_days:
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
            prepare_activity(table_row, fact)
            prepare_category(table_row, fact)
            prepare_tagnames(table_row, fact)

    def prepare_activity(table_row, fact):
        table_row['activity'] = fact.activity_name + actcatsep()

    def prepare_activities(table_row, activities, sep=_(', ')):
        table_row['activities'] = sep.join(
            [activity + actcatsep() for activity in sorted(activities)]
        )

    def prepare_actegories(table_row, actegories, sep=_(', ')):
        table_row['actegories'] = sep.join(sorted(actegories))

    def prepare_categories(table_row, categories, sep=_(', ')):
        table_row['categories'] = sep.join(
            [actcatsep() + category for category in sorted(categories)]
        )

    def prepare_category(table_row, fact):
        table_row['category'] = actcatsep() + fact.category_name

    def prepare_actegory(table_row, fact):
        table_row['actegory'] = fact.oid_actegory()

    # MAYBE/2020-05-18: Make the '@' symbol configable.
    def actcatsep(sep=_('@')):
        if for_journal:
            return sep
        return ''

    # +++

    def prepare_tagnames(table_row, fact):
        table_row['tags'] = assemble_tags(fact.tags)

    def prepare_tagname(table_row, fact):
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
        duration = format_fact_or_query_duration(fact, duration)
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

    def prepare_group_count(table_row, group_count):
        if not include_usage:
            return

        table_row['group_count'] = group_count

    def prepare_first_start(table_row, first_start):
        if not include_usage:
            return

        table_row['first_start'] = first_start

    def prepare_final_end(table_row, final_end):
        if not include_usage:
            return

        table_row['final_end'] = final_end

    # +++

    def prepare_description(table_row, fact):
        if not include_description or is_grouped:
            return

        table_row['description'] = fact.description or ''

    # ***

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
        gross_totals = [0, 0, None, None]
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
        if not include_duration:
            return

        # The SQLite aggregate result is in (julian)days, but the
        # timedelta is specified in seconds, so convert to the latter.
        fmt_duration = format_duration_days(gross_totals[i_cum_duration])
        table_row['duration'] = fmt_duration
        return fmt_duration

    def produce_gross_group_count(gross_totals, table_row):
        if not include_usage:
            return

        table_row['group_count'] = gross_totals[i_group_count]

    def produce_gross_first_start(gross_totals, table_row):
        if not include_usage:
            return

        table_row['first_start'] = gross_totals[i_first_start]

    def produce_gross_final_end(gross_totals, table_row):
        if not include_usage:
            return

        table_row['final_end'] = gross_totals[i_final_end]

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

    return _generate_facts_table()

