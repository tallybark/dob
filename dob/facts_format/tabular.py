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
    show_usage=False,
    hide_description=False,
    hide_duration=False,
    custom_columns=None,
    chop=False,
    table_type='friendly',
):
    table, headers, desc_col_idx = generate_facts_table(
        controller,
        results,
        row_limit,
        is_grouped,
        show_description=not hide_description,
        show_duration=not hide_duration,
        show_usage=show_usage,
        custom_columns=custom_columns,
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
    # Use singular column header when Act@Cat aggregated b/c group_tags.
    'tag': _("Tag"),
}


def generate_facts_table(
    controller,
    results,
    row_limit,
    is_grouped,
    show_description=True,
    show_duration=True,
    show_usage=False,
    custom_columns=None,
):
    """
    Prepares Facts for display in an ASCII table.

    Returns a (table, header) tuple. 'table' is a list of ``TableRow``
    instances, each representing a single Fact, or the summary of a
    group of Facts.
    """
    columns = []

    include_usage = show_usage or custom_columns

    # MAGIC_NUMBER 86400 seconds/day, to convert between timedelta
    # (seconds) and SQLite julianday computation (days).
    SECONDS_IN_DAY = 86400.0

    def _generate_facts_table():
        fact_results, gross_totals = unpack_results()
        headers, TableRow = prepare_columns(fact_results)

        table = []
        n_row = 0
        for result in fact_results:
            n_row += 1
            if row_limit > 0 and n_row > row_limit:
                break

            table_row = prepare_row(result)
            table.append(TableRow(**table_row))

        table_row = prepare_gross(gross_totals)
        if table_row is not None:
            empty_row = {key: '' for key in table_row.copy().keys()}
            table.append(TableRow(**empty_row))
            table.append(TableRow(**table_row))

        desc_col_idx = deduce_trunccol()

        return (table, headers, desc_col_idx)

    # ***

    def unpack_results():
        # The nark query result is always a tuple:
        # - The results, and the gross_totals.
        fact_results, gross_totals = results
        return fact_results, gross_totals

    def prepare_columns(fact_results):
        columns[:] = assemble_columns(fact_results)
        headers = [FACT_TABLE_HEADERS[column] for column in columns]
        TableRow = namedtuple('TableRow', columns)
        return headers, TableRow

    # ***

    def prepare_row(result):
        if not is_grouped and not include_usage:
            # The result is the result. Fake None values for the lack of any
            # aggregate values, so that we can blindly unpack variables next.
            result = [result]
            result.extend(group_cols_shim())
        # else, each result is a tuple: First the Fact, and then the
        #       aggregate columns (see FactManager.RESULT_GRP_INDEX).
        (
            fact,
            duration,
            group_count,
            first_start,
            final_end,
            activities,
            actegories,
        ) = result

        table_row = {}

        prepare_key(table_row, fact)

        prepare_start(table_row, fact)
        prepare_end(table_row, fact)
        prepare_activity_and_category(table_row, fact, activities, actegories)
        prepare_duration(table_row, fact, duration)
        prepare_group_count(table_row, group_count)
        prepare_first_start(table_row, first_start)
        prepare_final_end(table_row, final_end)
        prepare_description(table_row, fact)

        row_slice = unprepare_unmentioned_columns(table_row)

        return row_slice

    def group_cols_shim():
        return [None] * len(FactManager.RESULT_GRP_INDEX)

    # ***

    def assemble_columns(fact_results):
        if custom_columns:
            # Cull list of duplicates, retaining order.
            seen = set()
            seen_add = seen.add
            return [
                col for col in custom_columns
                if not (col in seen or seen_add(col))
            ]
        elif not is_grouped:
            return assemble_columns_single_fact()

        if fact_results:
            _fact, *any_aggregates = fact_results[0]
        else:
            any_aggregates = group_cols_shim()
        return assemble_columns_grouped_facts(any_aggregates)

    def assemble_columns_single_fact():
        columns = [
            'key',
            'start',
            'end',
            'activity',
            'category',
            'tags',
        ]
        if show_description:
            columns.append('description')
        if show_duration:
            columns.append('duration')
        return columns

    def assemble_columns_grouped_facts(any_aggregates):
        columns = []

        i_activities = FactManager.RESULT_GRP_INDEX['activities']
        i_actegories = FactManager.RESULT_GRP_INDEX['actegories']
        if any_aggregates[i_activities] not in [None, 0]:
            columns.append('category')
            columns.append('activities')
            columns.append('tags')
        elif any_aggregates[i_actegories] not in [None, 0]:
            columns.append('tag')
            columns.append('actegories')
        else:
            columns.append('activity')
            columns.append('category')
            columns.append('tags')

        if show_duration:
            columns.append('duration')

        if include_usage:
            columns.append('group_count')
            columns.append('first_start')
            columns.append('final_end')

        return columns

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

    def prepare_activity_and_category(table_row, fact, activities, actegories):
        if activities not in [None, 0]:
            prepare_category(table_row, fact)
            prepare_activities(table_row, activities)
            prepare_tagnames(table_row, fact)
        elif actegories not in [None, 0]:
            prepare_actegories(table_row, actegories)
            prepare_tagname(table_row, fact)
        else:
            prepare_activity(table_row, fact)
            prepare_category(table_row, fact)
            prepare_tagnames(table_row, fact)

    def prepare_activity(table_row, fact):
        table_row['activity'] = fact.activity.name

    def prepare_activities(table_row, activities):
        table_row['activities'] = _(', ').join(sorted(activities))

    def prepare_actegories(table_row, actegories):
        table_row['actegories'] = _(', ').join(sorted(actegories))

    def prepare_category(table_row, fact):
        if fact.category:
            category = fact.category.name
        else:
            category = ''
        table_row['category'] = category

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
        if not show_duration:
            return

        # Note that the 'duration' will be similar to fact.format_delta()
        # unless is_grouped, in which case 'duration' is an aggregate value.
        # But in either case, the 'duration' in the results is expressed in days.

        if not duration:
            delta_f = fact.format_delta(style='')
        else:
            style = ''  # Use pedantic_timedelta.
            # - MAYBE/2020-05-18: Set precision, etc.:
            #     delta_f = format_delta(
            #       duration, style='', field_width=0, precision=2, abbreviate=None,
            #     )
            # - The duration was computed by julianday math, so it's in days,
            #   and format_delta expects seconds, so convert to the latter.
            durasecs = duration * SECONDS_IN_DAY
            delta_f = format_delta(durasecs, style=style)
        table_row['duration'] = delta_f

    # +++

    def prepare_group_count(table_row, group_count):
        if not is_grouped and not include_usage:
            return

        table_row['group_count'] = group_count

    def prepare_first_start(table_row, first_start):
        if not is_grouped and not include_usage:
            return

        table_row['first_start'] = first_start

    def prepare_final_end(table_row, final_end):
        if not is_grouped and not include_usage:
            return

        table_row['final_end'] = final_end

    # +++

    def prepare_description(table_row, fact):
        if not show_description or is_grouped:
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

    def prepare_gross(gross_totals):
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
        prepare_gross_duration(gross_totals, table_row)
        prepare_gross_group_count(gross_totals, table_row)
        prepare_gross_first_start(gross_totals, table_row)
        prepare_gross_final_end(gross_totals, table_row)
        return table_row

    def prepare_gross_duration(gross_totals, table_row):
        if not show_duration:
            return

        i_duration = FactManager.RESULT_GRP_INDEX['duration']
        # The SQLite aggregate result is in (julian)days, but the
        # timedelta is specified in seconds, so convert to the latter.
        durasecs = gross_totals[i_duration] * SECONDS_IN_DAY
        delta_f = format_delta(durasecs, style='')
        table_row['duration'] = delta_f

    def prepare_gross_group_count(gross_totals, table_row):
        i_group_count = FactManager.RESULT_GRP_INDEX['group_count']
        table_row['group_count'] = gross_totals[i_group_count]

    def prepare_gross_first_start(gross_totals, table_row):
        i_first_start = FactManager.RESULT_GRP_INDEX['first_start']
        table_row['first_start'] = gross_totals[i_first_start]

    def prepare_gross_final_end(gross_totals, table_row):
        i_final_end = FactManager.RESULT_GRP_INDEX['final_end']
        table_row['final_end'] = gross_totals[i_final_end]

        return table_row

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

