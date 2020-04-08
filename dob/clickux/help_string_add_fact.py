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

"""Module to provide u18n friendly help text strings for our CLI commands."""

from gettext import gettext as _

from .help_strings import common_format


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
def ADD_FACT_COMMON(ctx):
    # Throw out a hint to use the pager, if not being used,
    # because this help document is dense.
    first_line = 'Help on Adding single Facts from the command line'
    if not ctx.find_root().params['pager']:
        first_line = _(
            'Wordy Add Fact Help / Try {codehi}{rawname} -P add -h{reset} for paged help'
        ).format(**common_format())

    # - Tricky, tricky: Click truncates first line at first period '.',
    # but if no dot found Click shows ellipses '...'. Show use a '.'.
    # - Also, each paragraph is reformatted to a common indentation
    # (the same amount of leading whitespace is removed from each line
    # in the string below, and then the lines are re-indented), but a
    # line above with just \b will skip re-indenting that paragraph.
    # After a \b, the first space of indent is converted to 2. So the
    # spacing after a \b might appear off by one.
    _help = _(
        """
        {first_line}.

        {underlined}Overview{reset}

        In {appname}, there are two easy ways to start and stop Facts:

        - You can use the interactive editor, by running {codehi}{rawname} edit{reset}.

        - You can use any of the Add Fact commands, documented below.

        {underlined}Concepts{reset}

        In {appname}, a {bold}Fact{reset} is essentially
        a document with a start time and an end time.
        It's a single timesheet entry.

        You can use {appname} to track time for your job,
        or maybe you use {appname} as a life hacking tool
        and you record every droll moment.

        However you use it, each Fact represents a block
        of time, with a start time, an end time (possibly
        left blank), your comments, and your tags.

        You can add Facts after you complete them,
        if you specify a start time and an end time.
        These Facts are considered {bold}complete{reset}.

        You can also {italic}{appname}{reset} in real time, if you
        specify a start time but not an end time.
        A Fact without an end time is considered the
        {bold}active{reset} Fact.

        To avoid chaos, you can only {bold}start{reset} one Fact at
        a time. So there will only be one active Fact at a time
        (or none).

        Once started, a Fact is {italic}active{reset} until you
        {bold}stop{reset} it, by setting its end time.

        {underlined}Why Are There So Many Add Fact Commands?{reset}

        There are a lot of commands that can be used to start a Fact.

        Each Add Fact command may perform either or both of these actions:

        - Stop the presently active Fact, if one was previously started.

        - Create and start a new Fact, making it the active Fact.

        Each of the different Add Fact commands performs a slightly
        different variation of those two actions, including how they
        set the start and end times.

        The variety of Add Fact commands should help you be more efficient.
        It should hopefully make adding Facts a little more fun, too, by
        making it feel more natural to interact with {appname}.

        {underlined}General Format{reset}

        The general Add Fact command format is:

         \b
         {codehi}{rawname} [COMMAND] [START-TIME] [to] [END-TIME] \\{reset}
             {codehi}[<activity>[@<category>]] [@<tag>...] [<description>]{reset}

        When you start or stop a Fact, you might specify one or two
        time values, which can be expressed using a timestamp
        (e.g., "2019-01-23"), or using more natural language
        (e.g., "5 mins. ago").

        - See {wordhi}{underlined}Time Format{reset}, below, for more help.

        When you start a new Fact, you can optionally specify
        an Activity, a Category, Tags, and a Description.

        - See {wordhi}{underlined}Meta Formats{reset}, below, for more help.

        Not all commands accept the start or end time arguments.

        Here's a look at which commands expect which time arguments.

         \b
         Command   Start   End   Example
         -------   -----   ---   -------
         {codehi}now{reset}          No    No   {codehi}{rawname} now Baking cookies.{reset}
         {codehi}at{reset}          Yes    No   {codehi}{rawname} at -10m: Eating cookies.{reset}
         {codehi}from{reset}        Yes   Yes   {codehi}{rawname} from 5:00 PM to 6:00 PM Workin' out.{reset}
         {codehi}to{reset}           No   Yes   {codehi}{rawname} to 5 mins. ago: Finishing task.{reset}
         {codehi}then{reset}        Opt    No   {codehi}{rawname} then I started a new project.{reset}
         {codehi}still{reset}       Opt    No   {codehi}{rawname} still Built Part 1, now Part 2.{reset}
         {codehi}after{reset}       Opt    No   {codehi}{rawname} after +5m: Left for home.{reset}

        Some hints:

        - The {codehi}from{reset} command expects 'to' between the start and end times.

        - If you do not specify a time when calling
        {codehi}then{reset}, {codehi}still{reset}, or {codehi}after{reset},
        the command will assume the time is "now" (the current machine time).
        The {codehi}now{reset} command always assumes the time is "now".

        - The {codehi}to{reset} command does not start a new Fact.
        It stops the active Fact, or if there is no active Fact,
        it starts a new Fact at the time when the last Fact ends
        and ends the new Fact at the time specified.

        - The {codehi}from{reset} command also does not start
        a new Fact. It creates a new Fact, but completes it
        (sets both the start time and the end time).

        - The {codehi}now{reset} and {codehi}at{reset} commands only
        start a new Fact. Alternatively, the
        {codehi}then{reset}, {codehi}still{reset}, and {codehi}after{reset}
        commands also start a new Fact but also end the presently active Fact.

        {underlined}Continuous Tracking{reset}

        Be aware that stopping the active Fact might lead you to inadvertently
        create time gaps in the data.

        For instance, suppose you call {codehi}{rawname} now{reset} to
        start a new Fact, and then later you {codehi}{rawname} stop{reset}
        to complete the Fact.

        After that, if you call {codehi}{rawname} now{reset} to start
        a second Fact, there will be a gap in the
        data from between the time you called {codehi}stop{reset} and the
        time you executed the second {codehi}now{reset}.

        A better method, which creates a seamless Fact lineage,
        is to never use {codehi}{rawname} stop{reset},
        and to always maintain an active Fact,
        or to always start new Facts using the end time of the latest completed Fact.

        A simple example is always using {codehi}now{reset}.
        If you run {codehi}{rawname} now{reset} once, when you first
        install {appname} and begin dobbing, you could just call
        {codehi}{rawname} now{reset} again whenever you want to create
        and start a new Fact.

        The {codehi}now{reset} command will close whatever Fact is
        active before starting a new active Fact, ending the old
        Fact with the same time used to start the new Fact.

        As another example, if you switched what you were working
        on but forgot to dob it, you could specify the time in the
        past when the old Fact ends and the new Fact starts, e.g.,

         \b
         {codehi}{rawname} at -1h: Built a thing!{reset}

        As yet another example, if you already stopped a Fact,
        you could create a new Fact that starts when the
        stopped Fact ends
        by using the {codehi}{rawname} then{reset} command,
        which will create a new Fact and set the start time to the end
        time of the most recently completed Fact. E.g.,

         \b
         {codehi}{rawname} then Built another thing!{reset}

        As a general rule, if an Add Fact command both starts a new Fact
        and stops an old Fact, the stopped Fact will always end exactly
        when the new Fact starts. This maintains a seamless, linear Fact
        database. If you want to create gaps in the data, you can
        use {codehi}stop{reset},
        or you can use the {codehi}to{reset}
        command with a relative negative time.

        {underlined}How to Use Activity, Category, and Tags{reset}

        Each Fact can be assigned to one Activity, and each Activity
        belongs to one Category. (So you could have two Activities with
        the same name, but in different Categories.)

        You can assign multiple Activities to the same Category to group
        Activities together.

        The Activity and Category for a Fact, colloquially called an
        {bold}act@gory{reset}, is useful for generating reports.

        Because each Fact can only be assigned one Activity and one Category
        combination, {rawname} can easily group Facts based on their
        Activity and Category to generate reports and to calculate statistics.

        You can also filter reports and search Facts using act@gories.

        Each Fact can also be assigned as many tags as you like.

        Tags are also useful for searching Facts,
        and Tags are useful for generating reports,
        but they're more work than relying on the {italic}act@gory{reset},
        because you need to specify the list of tags on which to report.
        Also, because you can apply more than one tag to a Fact,
        a Fact might unintentionally be used in multiple parts
        of a report or statistics calculation.

        {underlined}Time Format{reset}

        The start and end time arguments can each be either a timestamp,
        or a friendly string.

        - A timestamp can be as simple as {codehi}HH:MM{reset}
        to specify hours and minutes of the present day.

        - A timestamp can also include a
        {codehi}YYYY-MM-DD{reset}-formatted
        year, month, and day.

        - A friendly string is a human-readable phrase
        such as "now", "yesterday", "2 hours ago", etc.

        The Time Format must conform to one of the following rules:

         \b
         Format            Description
         ------            -----------
         {codehi}HH:MM{reset}             Clock time of present day, in 24 H military time.
         {codehi}HH:MM [AM|PM]{reset}     Clock time of present day, in 12 H civilian time.
         {codehi}YYYY-MM-DD HH:MM [AM|PM]{reset}
                           Year, month, day, and clock time.
         {codehi}-MM[m|h]{reset}          Minutes or Hours before "now", or nearest later Fact.
         {codehi}+MM[m|h]{reset}          Minutes or Hours after start or end nearest to "now".
         <friendly-time>   "1 week ago", "45 mins ago", "yesterday @ 3 PM", etc.

        - To be clear, {codehi}[AM|PM]{reset} means use either
        {codehi}AM{reset} or {codehi}PM{reset}.

        {underlined}Relative Time{reset}

        To really confuse you, dear reader, if you're not already overwhelmed,
        note that a positive or negative relative time duration can be used
        to specify the time.

        A negative duration generally resolves relative to "now", e.g.,
        when using an add Fact command, using "-1h" resolves to one hour
        before the current machine time.

        A positive duration used when adding a new Fact, alternatively,
        resolves relative to the start or end time of another Fact in
        the database. When using an add Fact command, a positive duration
        is computed relative to either the start time of the active Fact,
        or to the end time of the most recently completed Fact.

        For instance, if there is no active Fact, you could start
        one relative to when the latest Fact was completed, e.g., to
        start a new Fact 1 hour after the latest Fact was ended, run

         \b
         {codehi}{rawname} at +1h: Back at it.{reset}

        Alternatively, to reference the start time of the active
        Fact, say, to complete the active Fact and make it exactly
        one hour long, and to also append text to the description,
        run:

         \b
         {codehi}{rawname} to +1h: Finished task.{reset}

        Without getting too into the weeds, we'll also let you know
        that the {codehi}import{reset} command understands
        {italic}compounding{reset} relative times.

        E.g., suppose you were not able to dob until the day ended,
        and you wanted to record 3 tasks. The first task took 1 hour,
        the second task took 2 hours, and the third task took 3 hours.
        You could create an input stream with the three entries
        and then import that:

         \b
         {codehi}cat <<EOF |{reset}
         {codehi}{rawname} at 09:00 AM: Working on Task 1.{reset}

         \b
         {codehi}{rawname} at +1h: Working on Task 2.{reset}

         \b
         {codehi}{rawname} from +2h to +3h: Working on Task 3.{reset}
         {codehi}EOF{reset}
         {codehi}dob import{reset}

        Note that the {codehi}+3h{reset} end time of the third Fact
        will not be computed until after the start time ({codehi}+2h{reset})
        is computed, and that the length of the third Fact is 3 hours, not 1
        (i.e., it doesn't start 2 hours after the Fact before it, and then
        end 3 hours after the Fact before it; it starts 2 hours after the
        Fact before it, and then it ends 3 hours after it starts!).

        In general, these two rules apply to positive relative times:

        - For an end time, a positive relative time is relative to
        the same Fact's start time.

        - For a start time, a positive relative time is relative
        to the end time of the Fact before it.

        A negative relative time, on the other hand, will have the
        opposite properties:

        - If used for a start time, a negative relative time will
        be relative that that Fact's end time, or to "now", if there
        is no end time. (Except during import, than a negative relative
        time might be relative to the Fact that follows it!)

        - If used for an end time, a negative relative time is
        relative to "now" (except, again, for import, and then it's
        relative to the Fact after it).

        {underlined}Meta Formats{reset}

        {underlined}Act@Gory{reset}

        The Activity name and Category name are combined into one
        argument when specified on the command line. Use the at
        symbol, {codehi}@{reset}, to separate the two values (so
        you can use spaces in your Activity and Category names,
        but not the @ symbol!).

        HINT: Each Category contains one or more Activities, and each
        Activity belongs to one or more Categories, but each Activity
        will only be associated with any one Category at most once.

        For example, you could use the Activity to track different
        projects at work. Run an Add Fact command to start the first
        project using its name as the Activity name,

         \b
         {codehi}{rawname} now "Project-XYZ@My Job": Working on it.{reset}

        and then later run another command to start a new Fact with
        the other project name as the Activity name,

         \b
         {codehi}{rawname} now "Project-ABC@My Job": All Hands Meeting.{reset}

        In dob, the act@gory and tags are somewhat interchangeable.

        For instance, considering the previous example,
        you could track the same two projects using tags,
        starting on the first project with:

         \b
         {codehi}{rawname} now "Work@My Job" @Project-XYZ: Working on it.{reset}

        and then starting the second project with:

         \b
         {codehi}{rawname} now "Work@My Job" @Project-ABC: Working on it.{reset}

        The one drawback to using tags is that you might have to
        specify a few more options to the report and search commands
        to achieve what you can do less verbosely with Activities and
        Categories.

        However, if you work on lots of different projects that you'd
        like to track, by using tags you can keep a lot of noise from
        infesting your activities and categories as projects come and go.

        One way to decide when to use an Activity to track something
        and when to use a Tag is to determine how enduring is the
        think you are tracking.

        If you are tracking a particular project that you'll complete
        in the next weeks or months, consider using a tag.

        If you are tracking an event that is constantly recurring,
        such as time spent commuting to and from work, consider
        using an Activity (and Category, i.e., an act@gory).

        {underlined}Tags{reset}

        You can specify zero or more Tags for each Fact.

        You must delimit each tag argument. The tag delimiter will
        not be included as part of the tag.

        It's easiest to use the {codehi}@{reset} symbol to denote tags,
        rather than using {codehi}#{reset}, like you'd see in social media.
        This is because you'd probably need to escape the pound symbol to use it.
        That is, because Bash and other shells interpret an octothorpe
        as the start of a comment, you have to use quotes around it ({codehi}"#"{reset})
        or escape it ({codehi}\#{reset}) to use it.

        E.g., these are all acceptable tags:

         \b
         {codehi}@tag1 @"tag2 too" "#tag3" @give-it-up-for-tag4 \#tag5 '#'tag6{reset}

        Also be aware that you need to use quotes if a tag contains whitespace.
        E.g., these are all acceptable ways to specify tags:

         \b
         {codehi}@foo-bar{reset}, {codehi}"@foo bar"{reset} and {codehi}@"foo bar"{reset}

        But without the quotes, e.g.,

         \b
         {codehi}@foo bar{reset}

        the parser would identify a tag named "foo" for the Fact,
        and the second part, "bar", would be seen as the description.

        {underlined}Description{reset}

        A description of the Fact for the particular Activity being performed
        at the indicated time. Which is to say, journal away! This is your
        worklog entry, or your diary entry, or whatever it is you want to
        call it. Record what you're doing, or what you're feeling, dig it?

        {underlined}Examples{reset}

        - Start your day by starting a Fact under the "Waking up"
        Activity in the "Personal" category. Suppose you got up
        at 8am and got to your machine 20 minutes later, you could
        {rawname}:

         \b
         {codehi}{rawname} at 08:00 Waking up@Personal Woke up. \\{reset}
         {codehi}  Slept pretty well, except for the spiders again.{reset}

        - Get ready for work, and then use the 'to' command and an empty '@'
        symbol to indicate the same Activity being closed.

         \b
         {codehi}{rawname} to 08:45 @ Getting ready for work.{reset}

        - Commute to work, then dob in the missing gap.
        Use a tag to remember what mode you used to travel.

         \b
         {codehi}{rawname} until 09:15 Commuting \#bike{reset}

        - Start working on a ticket.

         \b
         {codehi}{rawname} on PROJ-1234@Work Fixing all the bugs!{reset}

        - Go to lunch, but get back just in time to run to a meeting.

         \b
         {codehi}{rawname} from -30now @MEET-4567 @standup Barely made it to the meeting, oops!{reset}

         \b
         {codehi}{rawname} now @MEET-4567 @standup Barely made it to the meeting, oops!{reset}

        - Remember that you forgot to clock out for lunch and do that now.

         \b
         {codehi}{rawname} from 1130 to noon Eating@Personal #gram-it! Salad and fries.{reset}

        - Start working on another ticket and then remember to clock out of
        that earlier meeting. (HINT: `start` is an alias for `at`)

         \b
         {codehi}{rawname} start 30 mins ago '#PROJ-9876' @ Refactoring this mess.{reset}

        - All done for the day! Start a "Sleep" fact under "Personal".

         \b
         {codehi}{rawname} at 11:59 PM Sleep@Personal Time for bed!{reset}

        {underlined}Quick Reference{reset}

        Here's a quick look at which commands accept which time arguments,
        and how they behave.

         \b
         Command   Start   End   Stops    Default
                               Active?      Start
         -------   -----   ---   -----    ---------------------------
         {codehi}after{reset}       Opt    No     Y??    Last end time.
         {codehi}at{reset}          Yes    No     Yes    You must specify start.
         {codehi}from{reset}        Yes   Yes      Y?    You must specify both.
         {codehi}now{reset}          No    No     Yes    Always "now" time, when command run.
         {codehi}still{reset}       Opt    No     Yes    Last end time, or now; copies metadata.
         {codehi}then{reset}        Opt    No     Yes    Last end time, or now.
         {codehi}to{reset}           No   Yes     Yes    You must specify end time.
                                          If no active, new Fact starts at last end.

        """.format(first_line=first_line, **common_format())  # noqa: E501
    )
    return _help

