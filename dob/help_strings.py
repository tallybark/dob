# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

"""Module to provide u18n friendly help text strings for our CLI commands."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from nark.helpers.colored import fg, attr

from . import __arg0name__, __BigName__


# FIXME: Dehardcode: Use .format(appname=__arg0name__) herein!


# ***
# *** [BARE] Command help.
# ***

RUN_HELP = _(
    """
    {big_name} is a time tracker for the command line.

    You can use it to track how you spend your time as well as have it export your
    collected data into various output formats. Below you find a list of available
    commands. If you call them with the '--help' option you will be shown details
    on how to use the command and its supported arguments and parameters.

    In general and as usual: if you want to pass any arguments or options that
    contain whitespace, you will need to wrap them in quotation marks.

    Note: Global options (like -V and --color) must come before the command name.

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to
    redistribute it under certain conditions.
    Run `hamster copyright` and `hamster license` for details.



    """.strip().format(appname=__arg0name__, big_name=__BigName__)
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
# *** [INDUCTEE] help.
# ***

NEWBIE_HELP_WELCOME = _(
    """
{color}Welcome to dob!{reset}
{color}==============={reset}
    """
).strip().format(
    color=(fg('spring_green_2a') + attr('bold')),
    # color=(fg('turquoise_4') + attr('bold')),
    # color=(fg('magenta_2a') + attr('bold')),
    # color=(fg('dark_orange_3b') + attr('bold')),
    reset=attr('reset'),
)


def section_heading(title):
    return """{color}{title}
{line_color}{sep:{sep}<{len_title}}{reset}""".format(
        title=title,
        sep='-',
        len_title=len(title),
        # color=fg('spring_green_2a'),
        # color=fg('dark_orange'),
        # color=fg('turquoise_4'),
        # line_color=fg('grey_78'),
        # line_color=fg('light_blue'),
        line_color='',
        color='',
        reset=attr('reset'),
    )


NEWBIE_HELP_ONBOARDING = _(
    # If you have an existing Hamster database,
    # we've got you covered!
    """
{banner}

Let's get you setup!

{upgrade_title}
{paragraph_color}
To learn how to upgrade, run:{reset}

  {cmd_color}{appname} upgrade{reset}

{init_title}
{paragraph_color}
To create a fresh, empty database, run:{reset}

  {cmd_color}{appname} init{reset}
"""
).format(
    appname=__arg0name__,
    banner=NEWBIE_HELP_WELCOME,
    upgrade_title=section_heading(_('Import existing facts')),
    init_title=section_heading(_('Start from scratch')),
    # cmd_color=(fg('dodger_blue_1')),
    cmd_color=fg('spring_green_2a'),
    # paragraph_color=fg('grey_78'),
    paragraph_color='',
    reset=attr('reset'),
)


NEWBIE_HELP_CREATE_CONFIG = _(
    """
{banner}

Where's you config file??

FIXME: Provide example commands.

    """
).format(
    # appname=__arg0name__,
    banner=NEWBIE_HELP_WELCOME,
    # cmd_color=(fg('spring_green_2a') + attr('bold')),
    # reset=attr('reset'),
)


NEWBIE_HELP_CREATE_STORE = _(
    """
{banner}

Where's you database??

FIXME: Provide example commands.

    """
).format(
    # appname=__arg0name__,
    banner=NEWBIE_HELP_WELCOME,
    # mintgreen=(fg('spring_green_2a') + attr('bold')),
    # reset=attr('reset'),
)


# ***
# *** [INIT] Command help.
# ***

INIT_HELP = _(
    """
    """
)


# ***
# *** [CONFIG] Commands help.
# ***

CONFIG_GROUP_HELP = _(
    """
    """
)


CONFIG_CREATE_HELP = _(
    """
    """
)


# ***
# *** [STORE] Commands help.
# ***

STORE_GROUP_HELP = _(
    """
    """
)


STORE_CREATE_HELP = _(
    """
    """
)


STORE_PATH_HELP = _(
    """
    """
)


STORE_URL_HELP = _(
    """
    """
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
#FIXME: (lb): day_start is disabled by default (I never liked this weird legacy behavior)
# new workflow is to start 'now', eh?
#        * Missing *start time* will fall back to your configured 'day_start'
#          setting.
#        * Missing *end date* will be the day after today if 'day_start' is not
#          '00:00', else it will be today.
#        * Missing *end time* will be one second before your configured
#          'day_start' value.
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


USAGE_FACTS_HELP = _(
    """
    List all facts by usage.
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
# FIXME/2018-06-09: (lb): Fix this:
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
# *** [CREATE-FACT] Commands help.
# ***

# FIXME: Thoughts on format.
#        If always an '@' you could know if activity specified,
#           and not start of description.
#        OR: You could require that an Activity be specified!
#          (And you don't need category if it can be inferred; or if you
#           use a default.)
#          (You could say that you could have an Activity default, but I
#          don't want to encourage not categorizing your Facts, so require
#          an Activity -- if anything, a lazy user could either make a Bash
#          alias, or make a catch-all Activity, e.g.,
#           `hamster at now null I did something.`
#
#        For #tags, you could require that if multiple words, they're wrapped
#           in quotes.
#        Otherwise, if just single words, then you don't need that silly comma
#           in the factoid!
#        And also, you could easily mistake, say,
#          `hamster at now null #hashtag I went to market, but didn't buy anything`
#        for the hashtag: "hashtag I went to the market", which is what
#           the code currently does!
#
#        For timestamp, require hours and minutes; but allow any obvious delimiter.

# NOTE: In Click, \b prevents re-wrapping blocks of text using terminal width.
START_HELP_COMMON = _(
    # NOTE: Click replaces each line's leading whitespace with 2 spaces,
    #       so 4 leading spaces become 2. However, for whatever reason,
    #       the same is not true for lines with more than 4 leading spaces,
    #       e.g., a line with 6 leading spaces has its 6 leading spaces
    #       preserved. Oh, wait, each space after the 4th is converted into 2?
    """
    \b
    FACTOID:

    \b
    Describes the Fact being created, including the start time, the
    Activity, and maybe Category, any tags, and the fact description.

    \b
    The FACTOID has the following format:

    \b
    [<timestamp>] [<activity>[@<category>]] [<tags>] <description>

     \b
     <timestamp>
     An optional timestamp, or "now" if not specified.

     \b
     The timestamp may be in hour and minutes (for the present day);

      \b
      or it may also include the year, month, and day;

      \b
      or it may specify a human-readable, friendly time,
       such as "now", "yesterday", "2 hours ago", etc.

     \b
     The timestamp must match one of the following formats:

     \b
     'HH:MM'             Clock time of present day, in 24 H military time.
     'HH:MM (AM|PM)'     Clock time of present day, in 12 H civilian time.
     '-MM'               Minutes before now; useful when Fact just started.
     'YYYY-MM-DD HH:MM [AM|PM]'
                         Year, month, day, and clock time.
     <friendly-time>     "1 week ago", "45 mins ago", "yesterday @ 3 PM", etc.

    \b
    <activity>
    The name of the Activity with which to associate the Fact.
    This value is mandatory.

    \b
    <category>
    The Category associated with the Activity. If not specified, the
    first Category found (searching alphabetically) that contains the
    Activity will be used, or the last Category specified.

     \b
     HINT: Each Category contains one or more Activities, and each
     Activity belongs to one or more Categories, but each Activity
     will only be associated with any one Category at most once.

    \b
    <tags>
    Tags to apply to the Fact. These are optional.

     Each tag is usually delimited by an @ symbol, rather than a #,
     because Bash and other shells interpret an octothorpe as the
     start of a comment. However, you can use a # symbol if you use
     quotes around it, or if you escape the # symbol (e.g., '\#').

     E.g., these are all acceptable tags:

      @tag1 @"tag2 too" "#tag3" @give-it-up-for-tag4 \#tag5 '#'tag6

     \b
     HINT: Use quotes if a tag contains whitespace, e.g., <@foo-bar>,
     <"@foo bar">, and <@"foo bar"> are all acceptable, but <@foo bar>
     would be interpreted as the tag "foo", and the description, "bar".

    \b
    <description>
    A description of the Fact for the particular Activity being performed
    at the indicated time. Which is to say, journal away! This is your
    worklog entry, or your diary entry, or whatever it is you want to
    call it. Record what you're doing, or what you're feeling, dig it?

    \b
    EXAMPLES:

     \b
     # Start your day by starting a Fact under the "Waking up" Activity
     # in the "Personal" category:

     \b
     hamster at 08:00 Waking up@Personal Woke up. Slept pretty well, \\
     except for the spiders again.

     \b
     # Get ready for work, and then use the 'to' command and an empty '@'
     # symbol to indicate the same Activity being closed.

     \b
     hamster to 08:45 @ Getting ready for work.

     \b
     # Commute to work and then fill in the missing gap in hamster.
     # Use a tag to remember what mode you used to travel.

     \b
     hamster until 09:15 Commuting \#bike

     \b
     # Start working on a ticket.

     \b
     hamster on PROJ-1234@Work Fixing all the bugs!

     \b
     # Go to lunch, but get back just in time to run to a meeting.

     \b
     hamster now @MEET-4567 @standup Barely made it to the meeting, oops!

     \b
     # Remember that you forgot to clock out for lunch and do that now.

     \b
     hamster from 1130 to noon Eating@Personal #gram-it! Salad and fries.

     \b
     # Start working on another ticket and then remember to clock out of
     # that earlier meeting. (HINT: `start` is an alias for `at`)

     \b
     hamster start 30 mins ago '#PROJ-9876' @ Refactoring this mess.

     \b
     # All done for the day! Start a "Sleep" fact under "Personal".

     \b
     hamster at 11:59 PM Sleep@Personal Time for bed!

    """
)
#     \b
#     # Get ready for work, and then use the 'to' command and an empty '@'
#     # symbol to indicate the same Activity being closed.
#     #
#     # FIXME: Can you append to ongoing Fact with hamster-close?
#     #        Also, hamster-to should work on closed time windows.
#
#     \b
#     hamster to 08:45 @ Getting ready for work.


# FIXME: So that @ can be used for tags,
#        allow '/' to be used for activity@category,
#          e.g., activity/category.
#        You can still allow '@' because it would never
#        not follow the activity, or not be followed by
#        the category, e.g.,
#          act@cat act@ @ <== all acceptable
#          @foo <== always interpreted as tag

START_HELP_ON = _(
    """
    """
)


START_HELP_AT = _(
    """
    \b
    Adds a fact beginning now, or at specified time.

    \b
    Might also stop the current ongoing fact if one exists and the
    new fact starts after the current fact; or might change the stop
    time of an existing fact if the two facts' time windows overlap.

    {}
    """
).format(START_HELP_COMMON)


START_HELP_TO = _(
    """
    """
)


START_HELP_BETWEEN = _(
    """
    """
)


# ***
# *** [EDIT] Command help.
# ***

EDIT_GROUP_HELP = _(
    """
    Edit facts, activities, categories, or tags.
    """
)


EDIT_FACT_HELP = _(
    """
    Edit facts using your preferred \$EDITOR.
    """
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


# ***
# *** [IMPORT] Command help.
# ***

IMPORT_HELP = _(
    """
# FIXME/2018-05-12: (lb): Document hamster-import.
    """
)


# ***
# *** [COMPLETE] Command help.
# ***

COMPLETE_HELP = _(
    """Bash tab-completion helper."""
)


# ***
# *** [MIGRATE] Commands help.
# ***

MIGRATE_GROUP_HELP = _(
    """
    Perform database migrations.
    """
)


MIGRATE_CONTROL_HELP = _(
    """Mark a database as under version control."""
)


MIGRATE_DOWN_HELP = _(
    """Downgrade the database version by 1 script."""
)


MIGRATE_UP_HELP = _(
    """Upgrade the database version by 1 script."""
)


MIGRATE_VERSION_HELP = _(
    """Show the database migration version."""
)


MIGRATE_LEGACY_HELP = _(
    """Migrate a legacy "Hamster" database."""
)

