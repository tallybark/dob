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

from nark.helpers.emphasis import attr, bg, coloring, fg

from .. import __arg0name__, __package_name__
from ..config.manage import default_config_path
from ..config.urable import ConfigUrable
from ..copyright import assemble_copyright
from ..helpers import highlight_value

# Note that the help formatter reformats paragraphs when the help is
# displayed, to a width determined by the terminal and max_content_width.
# So the newlines you see in the text below will be removed and each
# paragraph will be reformatted with indents and new newlines inserted.
# - Your best bet to see how the text is formatted is to run the help.

# Note also that a lot of the help text is assembled at runtime, after
# dob has started and parsed command line arguments and configuration
# settings. This is because the global coloring() switch is off until
# after arguments are parsed and the config is read, and then it might
# be turned. But the way coloring works, ANSI is stripped when strings
# are assembled, as opposed to ANSI being stripped on output (the latter
# would make it easier to turn color on or off without having to rebuild
# strings, or to worry about when strings are generated; but our code is
# built the other way, so we have to wait for the coloring() question to
# be settled before building help text. Hence all the callbacks below.
#
# E.g., instead of seeing help text built like this:
#
#           SOME_HELP_TEXT = _("""Helps you.""")
#
#       you'll often see a builder method used instead, such as:
#
#           def SOME_HELP_TEXT(ctx):
#               return _("""Helps {color}you{reset}.""").format(...)

# ***
# *** [COMMON] Oft-used format() args.
# ***


def common_format():
    # (lb): Eh: This is a method because ENABLE_COLORS is False on startup,
    # and fg and attr will return empty strings if called when module is
    # sourced. So wait until help strings are built and it's known if color
    # or not.
    common_format = {
        'appname': highlight_value(__package_name__),
        'rawname': __package_name__,
        'codehi': (fg('turquoise_2') or ''),
        'reset': (attr('reset') or ''),
        'italic': attr('italic'),
    }
    return common_format


# ***
# *** [BARE] Command help.
# ***

def RUN_HELP_WHATIS():
    _help = _(
        """
        {appname} is a time tracker for the command line.
        """.strip().format(**common_format())
    )
    return _help


def RUN_HELP_TRYME():
    _help = _(
        """
        - Try the demo to get acquainted with dob quickly,

          {codehi}{rawname} demo{reset}
        """.strip().format(**common_format())
    )
    return _help


def RUN_HELP_HEADER():
    _help = _(
        """
        {what_is}

        {try_me}
        """.strip().format(
            what_is=RUN_HELP_WHATIS(),
            try_me=RUN_HELP_TRYME(),
            **common_format()
        )
    )
    return _help


def RUN_HELP_TLDR():
    _help = _(
        """
        {what_is}

        - To read lots more help, run the help command,

          {codehi}{rawname} help{reset}

        - To learn to dob quick and easy, try the demo,

          {codehi}{rawname} demo{reset}

        \b
        {copyright}
        """.strip().format(
            what_is=RUN_HELP_WHATIS(),
            try_me=RUN_HELP_TRYME(),
            copyright='\b\n        '.join(assemble_copyright()),
            **common_format()
        )
    )
    return _help


def RUN_HELP_COMPLETE():
    _help = _(
        """
        {run_help_header}

        - Use {italic}help{reset} with any command to learn more, e.g.,

          {codehi}{rawname} init --help{reset}

          {codehi}{rawname} help init{reset}

          {codehi}{rawname} edit -h{reset}

        - Put global options {italic}before{reset} the command name, e.g.,

          {codehi}{rawname} --no-color details{reset}

        - See how {rawname} can {italic}hack your life{reset} using plugins,

          {codehi}{rawname} plugins avail{reset} [FIXME: No such cmd!]

        - Some commands have aliases, shown in (parentheses) below, e.g.,

          {codehi}{rawname} details{reset} {equalityop} {codehi}{rawname} info{reset}

        - For code rights and legal info, review the {copyrt_sym} and {scroll_sym},

          {codehi}{rawname} copyright{reset}

          {codehi}{rawname} license{reset}
        """.strip().format(
            run_help_header=RUN_HELP_HEADER(),
            equalityop=coloring() and '≡' or '==',
            copyrt_sym=coloring() and '©' or 'copyright',
            scroll_sym=coloring() and '📜' or 'license',
            **common_format()
        )
    )
    return _help


def RUN_HELP_OVERVIEW(ctx):
    if (
        (ctx.command.name == 'run')
        and (
            ctx.invoked_subcommand
            or ctx.help_option_spotted
        )
    ):
        return RUN_HELP_COMPLETE()
    return RUN_HELP_TLDR()


# ***
# *** [HELP] Command help.
# ***

HELP_HELP = _(
    """
    Prints the help for the application or for the specified command.
    """
)


# ***
# *** [VERSION] Command help.
# ***

VERSION_HELP = _(
    """
    Prints the interface and library versions.
    """
)


# ***
# *** [LICENSE] Command help.
# ***

LICENSE_HELP = _(
    """
    Prints the software license.
    """
)


# ***
# *** [LICENSE] Command help.
# ***

COPYRIGHT_HELP = _(
    """
    Prints the software copyright.
    """
)


ABOUT_COMMAND_HELP = _(
    """
    Alias of 'copyright' command.
    """
)


# ***
# *** [DETAILS] Command help.
# ***

DETAILS_HELP = _(
    """
    Prints details about the runtime environment.
    """
)


DETAILS_TMI_HELP = _(
    """
    Show AppDirs paths, too.
    """
)

# ***
# *** [ENVIRONS] Command help.
# ***

ENVIRONS_HELP = _(
    """
    Prints shell-sourceable details about the runtime environment.

    Useful for setting up shell scripting, e.g.,

       \b
       eval "$({} environs)"
       echo $DOB_CONF
    """.format(__arg0name__)
)


# ***
# *** [DEBUG] Command help.
# ***

DEBUG_HELP = _(
    """
    """
)


# ***
# *** [DEMO] Command help.
# ***

# Ha! This ANSI gets stripped. But not if we callback.
# I wonder if because we set color off by default now,
# then enable... or maybe because we set it at all -- I
# just don't remember this being an issue last few days.
# -2019-11-19 05:47.
DEMO_HELP_XXX = _(
    """
    Teaches you how to {rawname} -- {ital}Run this first!{reset}
    """
).strip().format(
    rawname=__package_name__,
    ital=attr('italic'),
    reset=attr('reset'),
)
def DEMO_HELP(ctx):
    _help = _(
        """
        Teaches you how to {rawname} -- {ital}Run this first!{reset}
        """
    ).strip().format(
        rawname=__package_name__,
        ital=attr('italic'),
        reset=attr('reset'),
    )
    return _help


# ***
# *** [INDUCTEE] help.
# ***

def NEWBIE_HELP_WELCOME(ctx):
    _help = _(
        """
        {color}┏━━━━━━━━━━━━━━━━━┓{reset}
        {color}┃ Welcome to dob! ┃{reset}
        {color}┗━━━━━━━━━━━━━━━━━┛{reset}
        """
    ).strip().format(
        color=(fg('spring_green_2a') + attr('bold')),
        # color=(fg('turquoise_4') + attr('bold')),
        # color=(fg('magenta_2a') + attr('bold')),
        # color=(fg('dark_orange_3b') + attr('bold')),
        reset=attr('reset'),
    )
    return _help


def section_heading(title):
    return _(
        """
        {color}{title}
        {line_color}{sep:{sep}<{len_title}}{reset}
        """
    ).strip().format(
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


def NEWBIE_HELP_ONBOARDING(ctx):
    _help = _(
        """
        {banner}

        Let’s get you setup!

        {init_title}
        {paragraph_color}
        To create a fresh, empty database, run:{reset}

          {cmd_color}{appname} init{reset}

        {upgrade_title}
        {paragraph_color}
        To learn how to upgrade from a previous version (of dob, or hamster), run:{reset}

          {cmd_color}{appname} migrate{reset}

        {demo_title}
        {paragraph_color}
        If you’d like to demo the application first with some example data, run:{reset}

          {cmd_color}{appname} demo{reset}
        """
    ).format(
        appname=__arg0name__,
        banner=NEWBIE_HELP_WELCOME(ctx),
        upgrade_title=section_heading(_('Import existing facts')),
        init_title=section_heading(_('Start from scratch')),
        demo_title=section_heading(_('Demo Dob')),
        # cmd_color=(fg('dodger_blue_1')),
        cmd_color=fg('spring_green_2a'),
        # paragraph_color=fg('grey_78'),
        paragraph_color='',
        reset=attr('reset'),
    )
    return _help


def NEWBIE_HELP_CREATE_CONFIG(ctx, cfg_path):
    _help = _(
        """
        {errcol}ERROR: No config file found at: “{cfg_path}”{reset}

        Where's your config file??

        Verify and correct the configuration file path.

        The configuration file defaults to:

            {default_config_path}

        but you can override it using an environ:

            {envkey}=PATH

        or by specifying a global option:

            -C/--configfile PATH

        If you are certain the path is correct and you want to create
        a new configuration file at the path specified, run init, e.g.,:

            {rawname} -C "{cfg_path}" init
        """
    ).strip().format(
        # FIXME/2019-11-19 14:42: Make wrapper for format() with some common colors defined.
        # - Maybe change errors to white on red, like here,
        #   but only for white on black terms (based on some setting?).
        errcol=(bg('red_1') + attr('bold')),
        reset=attr('reset'),
        rawname=__package_name__,
        cfg_path=cfg_path,
        default_config_path=default_config_path(),
        envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
    )
    return _help


def NEWBIE_HELP_CREATE_STORE(ctx):
    _help = _(
        """
        {banner}

        Where's you database??

        FIXME: Provide example commands.

        """
    ).strip().format(
        # appname=__arg0name__,
        banner=NEWBIE_HELP_WELCOME,
        # mintgreen=(fg('spring_green_2a') + attr('bold')),
        # reset=attr('reset'),
    )
    return _help


# ***
# *** [INIT] Command help.
# ***

def INIT_HELP_OVERVIEW(ctx):
    controller = ctx.obj
    _help = _(
        """
        Ensures that the config file and data store exist.

        - Unless it exists, init will create a default configuration at:

            {default_config_path}

        - Unless it exists, init will create an empty database file at:

            {cfg_db_path}

        The config influences other runtime values you can see by running:

            {codehi}{rawname} details{reset}

        """.format(
            default_config_path=highlight_value(default_config_path()),
            cfg_db_path=highlight_value(controller.config['db_path']),
            rawname=__package_name__,
            codehi=(fg('turquoise_2') or ''),
            reset=(attr('reset') or ''),
        )
    )
    return _help


# ***
# *** [CONFIG] Commands help.
# ***

def CONFIG_GROUP_HELP(ctx):
    controller = ctx.obj
    _help = _(
        """
        Commands for managing user configurable values.

        Some application behavior can be changed via config values.

        Config values can be persisted across invocation in a config
        file.

        You can also specify config values at runtime on the command line,
        or using environment variables.

        {underlined}Config File Location{reset}

        By default, {rawname} looks for a configuration file at:

            {default_config_path}

        - You can specify an alternative file location
        using the {codehi}{envkey}{reset} environment value.

          E.g., you could set the environment for just the command subshell like:

          \b
          {codehi}{envkey}=path/to/{rawname}.conf {rawname} COMMAND ...{reset}

          or you could export the environment variable first and then invoke {rawname}:

          \b
          {codehi}export {envkey}=path/to/{rawname}.conf{reset}
          {codehi}{rawname} COMMAND ...{reset}

        - You can alternatively specify the configuration file location
        using the {codehi}-C/--configfile{reset} global option, e.g.,
        using shorthand:

          \b
          {codehi}{rawname} -C path/to/{rawname}.conf COMMAND ...{reset}

          or using --option=value longhand:

          \b
          {codehi}{rawname} --configfile=path/to/{rawname}.conf COMMAND ...{reset}

        {underlined}Config Value Precedence{reset}

        - If no config value is specified for a setting, {rawname}
        uses a default value.

        - If a config value is found in the config value, that value
        takes precedence over the default value.

        - If a corresponding environment variable for the config value
        is found, that value is preferred over the value from the file.

          - The environment variable for each setting is formed from
        a prefix, {codehi}DOB_CONFIG_{reset}, followed by the uppercase
        section name and the uppercase setting name.

          E.g., here's how to specify the db_engine setting using its
        environment variable:

          \b
          {codehi}DOB_CONFIG_BACKEND_DB_ENGINE=sqlite {rawname} stats{reset}

        - If a config value is specified via the command line, that value is
        preferred over all other values.

          - You can specify config values using the {codehi}-c/--config{reset}
        option, e.g.,

          \b
          {codehi}{rawname} -c backend.db_engine=sqlite stats{reset}

        {underlined}Config Command Overview{reset}

          - You can edit the config file directly, or (better yet) you can
        use the {codehi}dob set{reset} command to change its values.
        E.g., to enable coloring whenever you use {rawname}, run:

          \b
          {codehi}{rawname} config set client term_color True{reset}

          or omit the section name (because {rawname} is smart) and run instead:

          \b
          {codehi}{rawname} config set term_color True{reset}

          - If you remove the config file, or if you delete values from it,
        don't worry, {rawname} will use default values instead.

          - You can recreate the config file (and overwrite the existing file)
        with defaults by:

          \b
          {codehi}{rawname} config create --force{reset}

          - The best way to learn about all configurable settings is to
        print the config table, which includes a helpful message for each
        option:

          \b
          {codehi}{rawname} config dump{reset}

          - If you think your config file is missing values, you can
        update it with missing settings by running (naturally) the
        update command:

          \b
          {codehi}{rawname} config update{reset}

            - But you should not care about the contents of the config file
        if you stick to using {codehi}{rawname} config dump{reset} and
        {codehi}{rawname} config set{reset} commands.

            - Although you might care about the config file contents if you'd
        like to add comments to it, which is supported.
        """.format(
            underlined=attr('underlined'),
            default_config_path=highlight_value(default_config_path()),
            rawname=__package_name__,
            envkey=ConfigUrable.DOB_CONFIGFILE_ENVKEY,
            codehi=(fg('turquoise_2') or ''),
            reset=(attr('reset') or ''),
        )
    )
    return _help


CONFIG_CREATE_HELP = _(
    """
    Writes a new configuration file populated with default values.

    You can overwrite an existing configuration file using --force.
    """
)


CONFIG_CREATE_FORCE_HELP = _(
    """
    If specified, overwrite config file if is exists.
    """
)


CONFIG_DUMP_HELP = _(
    """
    Prints a list of configurable settings, including names, values, and help.
    """
)


CONFIG_GET_HELP = _(
    """
    Prints a configuration value from the config file.
    """
)


CONFIG_SET_HELP = _(
    """
    Writes a configuration value to the config file.
    """
)


CONFIG_UPDATE_HELP = _(
    """
    Write missing configuration values to the config file.
    """
)


# ***
# *** [STORE] Commands help.
# ***

STORE_GROUP_HELP = _(
    """
    Commands for managing the database file.
    """
)


STORE_CREATE_HELP = _(
    """
    Creates an empty database file.

    You can overwrite an existing database file using --force.
    """
)


STORE_CREATE_FORCE_HELP = _(
    """
    If specified, recreate data store if is exists.
    """
)


STORE_PATH_HELP = _(
    """
    Prints the database path.
    """
)


STORE_URL_HELP = _(
    """
    Prints the database URL.
    """
)


STORE_UPGRADE_LEGACY_HELP = _(
    """
    Migrates a legacy “Hamster” database to dob.
    """
)


STORE_UPGRADE_FORCE_HELP = _(
    """
    If specified, overwrite data store if is exists.
    """
)



# ***
# *** [STATS] Commands help.
# ***

STATS_HELP = _(
    """
    Prints stats about your data store.
    """
)


# ***
# *** [LIST] Commands help.
# ***

LIST_GROUP_HELP = _(
    """
    Prints facts, activities, categories, or tags.
    """
)


LIST_ACTIVITIES_HELP = _(
    """
    Prints all activities. Provide optional filtering by name.

    Prints all matching activities one per line.

    SEARCH: String to be matched against activity name.
    """
)


LIST_CATEGORIES_HELP = _(
    """
    Prints all existing categories, ordered by name.
    """
)


LIST_TAGS_HELP = _(
    """
    Prints all tags.
    """
)


LIST_FACTS_HELP = _(
    """
    Prints facts within a date range.

    Matching facts will be printed in a tabular representation.

    TIME_RANGE: Only fact within this time range will be considered.
    """
)


SEARCH_HELP = _(
    """
    Searches facts matching given time range and search term.

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
    Shows activity, category, or tag usage.
    """
)


USAGE_ACTIVITIES_HELP = _(
    """
    Prints all activities and their usage counts.
    """
)


USAGE_CATEGORIES_HELP = _(
    """
    Prints all categories and their usage counts.
    """
)


USAGE_TAGS_HELP = _(
    """
    Prints all tags by usage.
    """
)


USAGE_FACTS_HELP = _(
    """
    Prints all facts by usage.
    """
)


# ***
# *** [CURRENT-FACT] Commands help.
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


STOP_HELP = _(
    """
    Completes the *ongoing fact* at current time.
    """
)


CANCEL_HELP = _(
    """
    Cancels *ongoing fact*. I.e., stop the Fact and discard it without saving.
    """
)


CURRENT_HELP = _(
    """
    Prints the current, open-ended, ongoing fact, if there is one.
    """
)


NO_ACTIVE_FACT_HELP = _(
    """
    No active fact. Try {}starting{} a new fact first.
    """
).format(attr('italic'), attr('res_italic'))


NOTHING_TO_STOP_HELP = _(
    # """It doesn't look like there's any current Fact {}to{} stop."""
    """
    Sorry, bud, there's no ongoing Fact {}to{} stop.
    """
).format(attr('italic'), attr('res_italic'))


LATEST_HELP = _(
    """
    Prints the latest completed fact (i.e., with the latest end time).
    """
)


HELP_CMD_SHOW = _(
    """
    Prints the ongoing fact, or latest fact if there is no ongoing fact.
    """
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
    Starts a fact starting now.
    """
)


START_HELP_NOW = _(
    """
    Alias of 'on' command.
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


START_HELP_THEN = _(
    """
    """
)


START_HELP_STILL = _(
    """
    """
)


START_HELP_AFTER = _(
    """
    """
)


START_HELP_NEXT = _(
    """
    Alias of 'after' command.
    """
)


START_HELP_TO = _(
    """
    """
)


START_HELP_UNTIL = _(
    """
    Alias of 'to' command.
    """
)


START_HELP_FROM = _(
    """
    """
)


# ***
# *** [EDIT] Command help.
# ***

EDIT_GROUP_HELP = _(
    """
    Fires up the Carousel so you can edit Facts interactively.
    """
)


EDIT_FACT_HELP = _(
    """
    Fires up the Carousel so you can edit Facts interactively.
    """
)


# ***
# *** [EXPORT] Command help.
# ***

EXPORT_HELP = _(
    """
    Exports facts and other interesting data you desire.
    """
)


# ***
# *** [IMPORT] Command help.
# ***

# FIXME/2018-05-12: (lb): Document hamster-import more fully.
# - This command is quite powerful, and it might be a good way
# to demonstrate how all the dob-on/dob-after/etc. commands work.
IMPORT_HELP = _(
    """
    Imports Facts from a text file using a natural syntax.

    Useful if you cannot use dob for a while but can
    maintain a text file. Or if you need to massage
    data from another source into dob, it's easy to
    prepare an import file that dob can read and use
    to make Facts in the database.
    """
)


# ***
# *** [COMPLETE] Command help.
# ***

COMPLETE_HELP = _(
    """
    Bash tab-completion helper.
    """
)


# ***
# *** [MIGRATE] Commands help.
# ***

MIGRATE_GROUP_HELP = _(
    """
    Upgrades the database after installing a new major release.
    """
)


MIGRATE_CONTROL_HELP = _(
    """
    Marks a database as under version control.
    """
)


MIGRATE_DOWN_HELP = _(
    """
    Downgrades the database version by 1 script.
    """
)


MIGRATE_UP_HELP = _(
    """
    Upgrades the database version by 1 script.
    """
)


MIGRATE_VERSION_HELP = _(
    """
    Shows the database migration version.
    """
)


# ***
# *** [--GLOBAL-OPTIONS] Global Options help. [run_cli.py]
# ***

GLOBAL_OPT_VERBOSE = _(
    """
    Be chatty. (-VV for more.)
    """
)


GLOBAL_OPT_VERBOSER = _(
    """
    Be chattier.
    """
)


GLOBAL_OPT_COLOR_NO_COLOR = _(
    """
    Color, or plain. (Default: Auto.)
    """
)


GLOBAL_OPT_PAGER_NO_PAGER = _(
    """
    Send output to pager, or not. (Default: No.)
    """
)


GLOBAL_OPT_CONFIG = _(
    """
    Override config setting(s) (may do multiple).
    """
)


GLOBAL_OPT_CONFIGFILE = _(
    """
    Alternative path to configuration file.
    """
)

