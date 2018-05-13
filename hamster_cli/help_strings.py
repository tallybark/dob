# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

"""Module to provide u18n friendly help text strings for our CLI commands."""


from gettext import gettext as _


# ***
# *** [BARE] Command help.
# ***


RUN_HELP = _(
    """
    'hamster-cli' is a time tracker for the command line.

    You can use it to track how you spend your time as well as have it export your
    collected data into various output formats. Below you find a list of available
    commands. If you call them with the '--help' option you will be shown details
    on how to use the command and its supported arguments and parameters.
    In general and as usual: if you want to pass any arguments or options that
    contain whitespace, you will need to wrap them in quotation marks.
    """
)


# ***
# *** [VERSION] Command help.
# ***


VERSION_HELP = _(
    """Show the version and exit."""
)


# ***
# *** [LICENSE] Command help.
# ***


LICENSE_HELP = _(
    """Show license information."""
)


# ***
# *** [DETAILS] Command help.
# ***


DETAILS_HELP = _(
    """List details about the runtime environment."""
)


# ***
# *** [LIST] Commands help.
# ***


LIST_GROUP_HELP = _(
    """
    List facts, activities, categories, or tags.
    """
)


LIST_ACTIVITIES_HELP = _(
    """
    List all activities. Provide optional filtering by name.

    Prints all matching activities one per line.

    SEARCH: String to be matched against activity name.
    """
)


LIST_CATEGORIES_HELP = _(
    """List all existing categories, ordered by name."""
)



LIST_TAGS_HELP = _(
    """
    List all tags.
    """
)


LIST_FACTS_HELP = _(
    """
    List facts within a date range.

    Matching facts will be printed in a tabular representation.

    TIME_RANGE: Only fact within this time range will be considered.
    """
)


SEARCH_HELP = _(
    """
    Search facts matching given time range and search term.

    'search_term': May be an arbitrary string that will be matched against
    existing facts activity names.

    'time_range': Limit returned facts to those starting within the given time
    window.  This information may be specified in the following format:
    '%Y-%m-%d %H:%M - %Y-%m-%d %H:%M'.

    {time_range_info}
    \b
    About time range formats:
    You may omit any date and/or time portion of that format, in which case we
    will complete the missing information as described further down.
    Alternatively you can just pass start time offset from now in minutes such
    as ' -XX' (where X are 'minutes before now) which will also apply our
    'completion strategy' to the end time related values. Please note that you
    if you specify a relative starting time you need to wrap it in quotation
    marks as well as lead with a whitespace in front of the '-' sign.

    \b
    How missing date/time information is completed:
        * Missing *start date* will fall back to 'today'.
        * Missing *start time* will fall back to your configured 'day_start'
          setting.
        * Missing *end date* will be the day after today if 'day_start' is not
          '00:00', else it will be today.
        * Missing *end time* will be one second before your configured
          'day_start' value.
    """
)


# ***
# *** [USAGE] Commands help.
# ***


USAGE_GROUP_HELP = _(
    """
    Show activity, category, or tag usage.
    """
)


USAGE_ACTIVITIES_HELP = _(
    """
    List all activities and their usage counts.
    """
)


USAGE_CATEGORIES_HELP = _(
    """
    List all categories and their usage counts.
    """
)


USAGE_TAGS_HELP = _(
    """
    List all tags by usage.
    """
)


# ***
# *** [CURRENT-FACT] Commands help.
# ***


START_HELP = _(
    """
    Start or add a fact.

    If you add a fact without providing sufficient information about its end a
    *ongoing fact* will be created to capture you current work. Only one such
    fact can be present at any given time. Please refer to *stop*, *cancel*
    and *current* commands for further information.

    \b
    RAW_FACT:
    'raw_fact'-string containing information about the Fact to be started.
    'raw_fact' may have the following components:
    <timeinfo> <activityname>@<categoryname> #<tag1> #<tag2>, <description>'

      \b
      <timeinfo>
      May have one of the following three formats: 'HH:MM', 'HH:MM-HH:MM' or
      ' -MM'.
        * 'HH:MM': Start time in hours and minutes.
        * 'HH:MM-HH:MM' Start and end time given in ours and minutes.
        * ' -MM' Start time given as 'minutes before *now*. Please be advised:
          You need to lead with a whitespace before the '-' sign or put ' -- '
          before the start of your raw_fact. For details refer to
          https://github.com/elbenfreund/hamster_cli/issues/108
      All times specified refer to *today*.

      \b
      <activity>
      Name of the activity. This is the name of the (potentially recurring)
      action you want to track. As an absolute minimum this needs to be
      present.

      \b
      <category>
      You assign activities to categories to group them together. Each
      activity/category combination is allowed only once. If you have to
      activitynames in two distinct categories however, they will be treated
      totaly independent however.

      \b
      <tag1>, <tag2>, etc
      Tags are currently unsupported.

      \b
      <description>
      A detailed description of that particular instance of performing this
      activity. Please note that that is not a description of the category or
      the activity in general but a way to provide additional context to this
      instance.

    \b
    START:
    When does the fact start? When specified this will override any start
    information present in the *raw fact*. This is usefull if you want to add
    a fact with a different date than today.

    \b
    END:
    When does the fact end? When specified this will override any end information
    present in the *raw fact*.
    """
)


STOP_HELP = _(
    """Stop tracking current fact saving the result."""
)


CANCEL_HELP = _(
    """Cancel *ongoing fact*. E.g stop it without storing in the backend."""
)


CURRENT_HELP = _(
    """Display current tmp fact."""
)


# ***
# *** [EXPORT] Command help.
# ***


EXPORT_HELP = _(
    """
    Export all facts of within a given time window to a file of specified format.

    FORMAT: Export format. Currently supported options are:
      'csv', 'tsv', 'xml' and 'ical'. Defaults to ``csv``.

    START: Start of time window.

    END: End of time window.
    """
)

