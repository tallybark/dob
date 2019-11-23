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

from .help_strings import common_format

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

# ***
# *** [CREATE-FACT] Commands help.
# ***

START_HELP = _(
    """
    Starts or adds a fact.

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

