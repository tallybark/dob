#######
History
#######

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |dob-viewer| replace:: ``dob-viewer``
.. _dob-viewer: https://github.com/hotoffthehamster/dob-viewer

.. |dob-prompt| replace:: ``dob-prompt``
.. _dob-prompt: https://github.com/hotoffthehamster/dob-prompt

.. |dob-bright| replace:: ``dob-bright``
.. _dob-bright: https://github.com/hotoffthehamster/dob-bright

.. |nark| replace:: ``nark``
.. _nark: https://github.com/hotoffthehamster/nark

.. |hamster-cli| replace:: ``hamster-cli``
.. _hamster-cli: https://github.com/projecthamster/hamster-cli

.. |ohmyrepos| replace:: OhMyRepos
.. _ohmyrepos: https://github.com/landonb/ohmyrepos

.. :changelog:

3.0.13 (2020-06-18)
===================

- Highlights: Much improved searching and reporting.

  - A brief overview of what's documented in greater detail below:

    - Add grouping (by Activity, Category, Tags, and/or start date).

      - For instance, group by Activity, Category, and Day to see
        how much time was spent on each Activity\@Category each day.

    - Add multi-column sorting.

      - For instance, group by Activity, Category, and Day, and sort
        by day and usage to see results ordered by which tasks had the
        most time spent on them recently.

    - Add search on Fact description.

      - For instance, find all Facts whose description contains one
        or more search terms.

    - Add Tag frequency distributions.

      - For instance, to see the number of times each Tag was used in
        each result group.

    - Add JSON output format.

      - For instance, to prepare data to transmit elsewhere, such as
        <third-party timesheet server>.

    - Support human-friendly relative dates (like '1 day ago').

      - E.g., ``dob find --since yesterday``.

    - Wire since/until options to Activity, Category, and Tag searches
      (via ``list`` and ``usage`` commands).

      - E.g., ``dob list activities --since 'last week'``.

    - New 'Journal' search results format, exemplified by the new
      ``dob report`` command.

      - Includes sparklines and Tag frequencies, e.g.::

          $ dob report
          Fri Jun 12  8.3 hours  ████▌    Development@Tally Bark  #dob(5)
                      2.5 hours  █▍       Cooking & Eating@Personal  #salad

- Details: Add more powerful search and report options.

  - Rename a few existing options and a handful of single-character
    options, and add a number of new options for the search commands
    (for the existing ``search``, ``list``, ``usage``, and ``export``
    commands, and for the new ``report`` command).

  - Bring parity to the ``list``, ``usage``, ``search`` and ``export``
    commands, such that they all support as many of the same options as
    reasonable.

  - Add new report grouping options:

    - New ``-A/--group-activity``, to group results by Activity.

    - New ``-C/--group-category``, to group results by Category.

    - New ``-T/--group-tags``, to group results by Tag names.

    - New ``-Y/--group-days``, to group by Fact start date (YYYYMMDD).

  - Allow multiple columns to be specified with ``-S/--sort/--order``.

  - Remove ``-D/--desc`` and ``-A/--asc`` options and rely instead on
    ``-D/--direction/--dir`` option, which can now be specified multiple
    times, to support specifying a separate sort order for each of the
    now-multiple-allowed ``-S/--sort/--order`` options.

  - Rename report option ``-g/--category`` to ``-c/--category`` (which
    restricts results to matching Category), so that the option name
    pneumonic is obvious.

  - Add new ``-t/--tag`` search match option, to complement existing
    ``-a/--activity`` and ``-c/--category`` search match options.

  - Add search term support, for matching against Fact description.

    - E.g., ``dob find foo`` will find all Facts with 'foo' in their
      description.

  - Add single-character options for ``--since`` and ``--until`` options:
    ``-s`` and ``-u``.

  - Disable deprecated report options, ``--hidden`` and ``--deleted``.

  - Rename option ``-u/--usage`` to ``-U/--show-usage``.

  - Rename option ``-s/--span/--no-span`` to ``-N/--hide-duration``.

  - New option, ``-P/--hide-description``, to omit the Fact description.

  - New option, ``-l/--column``, allows user to specify exactly what
    details to include in the report (otherwise a reasonable set of
    default columns is reported).

    - E.g., the command,

      ``dob list facts --group-tags -l 'tag' -l 'group_count'``

      will show two columns, 'Tag' and 'Uses', that indicate
      each Tag name used on the grouped Facts, as well as how
      many Facts it's used on, and excludes all other columns.

  - Add a new sparkline output value, to visually represent the 'duration'.

    - And add options to control the new sparkline output value:
      ``--spark-width``, ``--spark-total``, and ``--spark-secs``.

  - Rename option ``-r/--rule`` to ``-R/--factoid-rule``, for readability.

  - Replace poorly implemented ``-t/--truncate`` option with ``-W/--width``
    option, to restrict report table or Factoid line to specific width.

    - Also change Factoid report to default to compact view (no blank
      lines) when width is used.

      - E.g., ``dob find --since 'last week' --factoid --width 110``.

  - Rename poorly-named ``-w/--doc`` output format option to ``--factoid``
    (or use ``-f factoid``).

  - Add JSON output format option (specify with ``-f json``, ``--json``,
    or ``-J``).

  - Split table and markup formats from ``--format`` to a new option,
    ``--table-type/--type``.

    - Now the ``-f/--format`` option only includes the higher-level
      formats, which are also each mapped to their own option names,
      e.g., ``--journal`` is equivalent to ``--format journal``.

      This list of higher-level formats is:

      ``--journal``, ``--factoid``, ``--ical``, ``--csv``, ``--json``,
      ``--tsv``, ``--xml``, and ``--table``.

    - The new ``--table-type/--type`` option is used to specify a table
      or markup output format, and includes: html, mediawiki, rst, etc.

      - E.g., ``dob find --since 'last week' --table --type rst``.

  - Modify ``--table`` option to use the ``texttable`` package and disable
    ``tabulate`` and ``humanfriendly`` usage, because neither of those
    packages wraps cell values, so their tables are not guaranteed to be
    readable in one's terminal.

    - This is mapped to the default ``--table-type normal`` option.

  - Add new ``--broad-match/--broad`` option, for applying report command
    search terms to matching meta fields, too.

    - E.g., ``dob find --broad foo`` will find all Facts with 'foo' in
      their description, in their Activity name, in their Category name,
      or in one of their Tag names, including parts of any name. For
      instance, it would match an Activity named 'afoobar'.

      Whereas, e.g., ``dob find -a foo`` would only find Facts with an
      Activity named exactly 'foo'.

  - Allow multiple Activity, Category, and/or Tag filters.

    - Rather than only accepting one attribute name to filter search
      results, allow many (and OR the filters).

    - E.g., ``dob find -a foo -a bar`` will find all Facts with
      an Activity named with 'foo' or 'bar'.

  - Add new config value, ``term.row_limit``, to replace hardcoded terminal
    output row limit, but ignore if output is being redirected.

    - This avoids overwhelming the terminal with too much output, unless
      the user explicitly asks for it.

  - Align columns better in the table output format.

    - E.g., align 'duration' column on decimal places, and right-align
      other number columns.

   - New options to show or hide cumulative result totals in aggregate search.

- Feature: New ``dob report`` command shows time spent recently on each
  Activity\@Category, grouped by start date, and formatted using 'Journal'.

  - The ``report`` command is essentially an alias for the otherwise
    lengthy ``find`` command::

      dob find \
        --since 'last week' \
        --group-days \
        --group-activity \
        --group-category \
        --sort day \
        --dir asc \
        --sort time \
        --dir desc \
        --journal

- Extend all commands that output a table to support the other formats, too.

  - In addition to table format, now also support CSV, TSV, XML, etc.

  - This affects the ``list`` and ``usage`` commands, as well as the
    ``config show``, ``styles show``, ``rules show``, and ``ignore show``
    commands.

  - E.g., ``dob config dump --json``.

- Improve: Tweak other option names.

  - Rename ``-C/--color/--no-color`` to ``-X/--color/--no-color``, and
    rename ``-c/--config`` to ``-C/--config``, so that now all single-
    character global options, save for ``-v/--version``, are capitalized.

  - Rename import command option ``-X/--leave-backup`` to ``-b/--leave-backup``.

- Bugfix: Activity without Category crashes ``list activities``.

  - That is, for any Activity that has NULL for the Category.

- Bugfix: ``dob usage tags`` crashes.

- Bugfix: ``dob list`` sort option broken.

- Alias: New ``dob find`` command is alias to ``dob search`` command.

- Improve: Add abbreviated ``list`` and ``usage`` command type names.

  - E.g., ``dob list act`` is an alias for ``dob list activities``.

- Add ``--show-duration`` option to ``list`` command.

  - Because of the complementary nature of the ``list`` and ``usage``
    commands, add ``--show-duration`` to complement ``--hide-duration``,
    to be used with ``list`` commands to achieve ``usage``-like output.

- Improve: Make ``dob export`` only generate Factoid report.

  - Because that's the only format than can be imported.

  - Also, require than an output file be specified for the ``export``
    command, to better differentiate it from the ``search`` command
    (because ``search`` could otherwise be used instead of ``export``).

- Improve: In reports, distinguish between Category with no name, and NULL.

  - Specifically, if an Activity has no Category assigned, show '<NULL>'
    rather than the empty string, which itself is a valid Activity name.

- Improve: Tweak ``details`` command output so colons align.

- Simplify: Hide ``migrate`` command (which is currently not needed).

- Bugfix: Catch overflow error when day delta too large.
  [|dob-viewer|_]

  - For instance, if the user enters a jump command but with a date,
    e.g.,``20200615J``, when they meant to instead use the ``f`` command,
    not the ``J`` command, i.e., ``20200615f``, catch and recover
    gracefully from the ``timedelta`` overflow error.

- Improve: Make mash-quit on unsaved changes prompt opt-in.
  [|dob-viewer|_]

  - As a convenience to developers, mashing Ctrl-q would skip the
    save confirmation on exit; this feature is now opt in via the
    new config setting, ``dev.allow_mash_quit``.

- Improve: Show hidden config options when requested directly.
  [|dob-bright|_]

  - E.g., ``dob config dump foo bar`` would previously not show
    the config setting if ``foo.bar`` was marked ``hidden``.

- Improve: Add max-width option to ``Fact.friendly_str``.
  [|nark|_]

  - It previously applied to just the description, but now can be applied
    to the complete friendly string.

  - Also make ANSI-aware, so that strings with colors or ornamentation
    are not truncated prematurely.

- Improve: Use 'at ...' syntax for Factoid with no end, not ' to <now>'.
  [|nark|_]

  - So that the active Fact writ as a Factoid is parsable on import.

- Restrict: Raise error on search if SQLite is not the engine.
  [|nark|_]

  - This conflicts with the goal (set by hamster-lib, and loftily sought
    by nark) to support any DBMS, but the necessary SQL aggregate functions
    are DBMS-specific, and SQLite is all that's been plumbed in this release
    (to support the enhanced search and report features).

- Bugfix: Aggregate results for Facts with two or more Tags is incorrect.
  [|nark|_]

  - Usage and duration were being over-counted.

- Bugfix: Both ``antecedent`` and ``subsequent`` mishandle momentaneous Facts.
  [|nark|_]

3.0.12 (2020-04-28)
===================

- Bugfix: Windows: ``dob demo`` broken.
  [|dob|_]

- Bugfix: Windows: Run ``notepad.exe`` if ``EDITOR`` not set.
  [|dob-viewer|_]

  - Normally if ``EDITOR`` is not set, the system's ``sensible-editor``
    command will run Nano or Vi, neither of which is available on Windows.
    Consequently, on Windows, when ``EDITOR`` is not set, dob displays a
    warning, awaits acknowledgment, and then runs the Carousel again.

- Bugfix: Windows: Temporary file path broken because colon.
  [|dob-viewer|_]

- Bugfix: Windows: dob shows backup file symlink error.
  [|dob|_]

3.0.11 (2020-04-26)
===================

- Bugfix: Windows support, aka upgrade to sqlalchemy 1.3.
  [|nark|_]

- Bugfix: Ensure warnings not cleared before awaiting acknowledgment.
  [|dob-viewer|_]

- Bugfix: Config settings path shows incorrectly when displaying errors.
  [|dob-bright|_]

3.0.10 (2020-04-25)
===================

- Bugfix: ``dob edit`` fails when no config, rather than printing message.
  [|dob-bright|_]

  - Also affects other commands that require the config.

  - E.g., this happens if the user has not called ``dob init``.

    In other words, this affects new users.

- Bugfix: ``dob edit`` does nothing after ``dob init`` on empty database.
  [|dob|_]

  - User should not be forced to dob-add a Fact before running the
    interactive Carousel. Instead, we can start with a basic gap Fact.

- Bugfix: Config created by ``dob init`` crashes subsequent dob commands.
  [|nark|_]

  - The internal log level values were being writ to the config file,
    rather than the friendly level names.

- Bugfix: Config file errors crash dob.
  [|dob-bright|_]

  - But rather than just catch one error, print it, and exit,
    collect all errors, print them all, and then just keep chugging,
    choosing to use default values rather then exiting.

  - User will have option to bail before running Carousel, which now
    requires the user's acknowledgement of the errors.

- Bugfix: ``dob edit`` shows most recently edited Fact.
  [|dob|_]

  - It should show the most recent Fact. So sort by start.

- Bugfix: Print error rather than crash on ``$EDITOR`` fail.
  [|dob-viewer|_]

  - Use case: User sets their ``EDITOR`` environment variable to
    a bad path, or adds arguments (which is not supported -- but
    one could use an intermediate shell script wrapper to add args).

- Bugfix: Post-processors not called after dob-add.
  [|dob|_]

  - Use case: On Carousel save, the export-commit plugin post processor
    is triggered. The same should happen after editing/adding Facts through
    the ``dob add`` family of commands, e.g., ``dob from xx to xx: A test!``

- Bugfix: Part-specific styles not appearing until after focus.
  [|dob-viewer|_]

  - Use case: Run ``dob edit`` and note the start and end time widget
    styles. Now shift focus to one of the widgets, and then away.

    - Depending on how the style is configured, the look of the widget
      after shifting focus away from it does not look like how it
      originally looked.

- Regression: Cannot enter colon (for clock time) in time widgets.
  [|dob-viewer|_]

  - Solution: Only enable colon commands when content has focus.

- Feature: Set app background color via ``label = <>`` in styles.conf.
  [|dob-viewer|_]

  - PTK already assigns 'class:label' to every widget. This updates the
    style-clobbering calls to maintain the label. Thus, user could add,
    say, ``label = 'bg:#00AA66'`` to their ``styles.conf``, to give the
    app a uniform background color.

- Improve: Require confirmation after printing errors on Carousel startup.
  [|dob-viewer|_]

  - Instead of pausing after printing error messages, require user to
    confirm. Otherwise, user may not have time to read the errors. Also,
    after quitting Carousel, errors are still off-screen (up-screen).

- Improve: Make easier to base styles off 'night' and 'light' base styles.
  [|dob-viewer|_]

  - Rather than assign the base color to all classes, which makes it
    difficult to override them in styles.conf (because user is then
    forced to override the highest-order class for every widget),
    leave all the class styles empty except for the lowest ordered
    class, which is common to all widgets, class:label.

- Improve: Use no precision in 'Gap Fact of' text until duration > 60 seconds.
  [|dob-viewer|_]

  - Otherwise the footer status message updates too frequently,
    is too distracting.

- Improve: Warn when syntax errors found in style config.
  [|dob-viewer|_]

3.0.9 (2020-04-20)
==================

- Feature: New ``dob config edit`` command, to get straight to the point.
  [|dob|_]

- Feature: New ``dob styles`` commands.
  [|dob|_]

  - | ``dob styles --help``
    | ``dob styles create``
    | ``dob styles conf``
    | ``dob styles edit``
    | ``dob styles list``
    | ``dob styles show``

- Feature: New ``dob rules`` commands.
  [|dob|_]

  - | ``dob rules --help``
    | ``dob rules create``
    | ``dob rules conf``
    | ``dob rules edit``
    | ``dob rules list``
    | ``dob rules show``

- Feature: New ``dob ignore`` commands.
  [|dob|_]

  - | ``dob ignore --help``
    | ``dob ignore create``
    | ``dob ignore edit``
    | ``dob ignore list``
    | ``dob ignore show``

- UX: Prefer config-show over config-dump.
  [|dob|_]

- Docs: Add section on config file populate command.
  [|dob|_]

- Improve: Ensure plugins loaded on config-create, too.
  [|dob|_]

- Bugfix: Import ``FactsDiff`` display broken.
  [|dob-viewer|_]

- Bugfix: 'value-tags' class missing from hash-and-label tag parts' styles.
  [|dob-viewer|_]

- Feature: New ``dob styles`` commands.
  [|dob-viewer|_]

- Feature: New ``dob rules`` commands.
  [|dob-viewer|_]

- Feature: New ``dob ignore`` commands.
  [|dob-viewer|_]

- Feature: Make tags_tuples parts styleable (for ``git edit``).
  [|dob-viewer|_]

- Feature: Make factoid parts styleable (for ``git show``).
  [|dob-viewer|_]

- Tweak: Update 'night' style settings.
  [|dob-viewer|_]

- Enhance: Apply 'value-tags' class to tags diff parts.
  [|dob-viewer|_]

- API: Rename functions; move functions between libraries.
  [|dob-viewer|_]

- API: Update renamed config setting: ``stylit_fpath`` → ``rules_fpath``.
  [|dob-viewer|_]

- Improve: Option to exclude section column from config table.
  [|dob-bright|_]

- Improve: Do not assume ASCII table width.
  [|dob-bright|_]

- UX: Change difficult to read 'red' warning text to 'yellow'.
  [|dob-bright|_]

  (Though really should be made configurable. Yellow works
  better on a dark background.)

- Harden: Prevent stylize from failing on user input.
  [|dob-bright|_]

- API: Rename to avoid confusion/match other usage: ``stylit`` → ``rules``.
  [|dob-bright|_]

- Library: Refactor, Relocate, and DRY work.
  [|dob-bright|_]

- API: De-scope function for broader usage.
  [|nark|_]

- API: Rename function: oid_colorize → oid_stylize.
  [|nark|_]

3.0.8 (2020-04-17)
==================

- Docs: Document the interactive editor.
  [|dob|_]

- Improve: Remove requirement that custom paste config be numbered sequentially.
  [|dob-viewer|_]

3.0.7 (2020-04-16)
==================

- Feature: Let user define custom key bindings for pasting arbitrary factoids.
  [|dob-viewer|_]

  - I.e., user can map their own keys to setting Fact metadata,
    including the act\@gory, tags, and the description.

  - Usage: Add 2 settings to your user config for each custom mapping.

    - One setting specifies the Factoid to parse,
      and the other is the key binding to use.

    - Nest them under a new ``[custom-paste]`` section. Use the prefixes,
      ``factoid_`` and ``mapping_``, and start numbering from ``1``.

    - For instance, within ``~/.cache/dob/dob.conf``, here are
      some custom mappings::

          [custom-paste]

          # Paste act@gory and 2 tags:
          factoid_1 = "Tea@Personal: #biscuit #zinger"
          mapping_1 = f4

          # Paste act@gory, 1 tag, and a description (if not already set):
          factoid_2 = "Tickets@Project: #num-1234: Working on baloney."
          mapping_2 = f5

          # Paste a few tags (the @: is required):
          factoid_3 = "@: #tag-1 #tag-2"
          mapping_3 = f6

          # Paste a mere description:
          factoid_4 = "#this is not a tag"
          mapping_4 = f7

      Then, just press ``F4``, or ``F5``, etc., to apply to the current Fact.

      The user can choose whatever keybindings they want, and whatever metadata.

      Note that there's an arbitrary limit of 28 such custom paste commands.

  - See also ``dob add --help`` for a description of the Factoid format.

    Or just follow the formats in the example above.

- Feature: New command "shortcuts" (multiple command wrappers).
  [|dob-viewer|_]

  - One command to copy the current Fact meta and paste to the final Fact.

    - Currently mapped to ``Ctrl-e``.

  - One command to copy the current Fact meta, stop the final Fact,
    and paste to the new active Fact.

    - Currently mapped to ``V``.

  - One command to stop the final Fact, switch to the new active Fact,
    and prompt for the act\@gory.

    - Currently mapped to ``o``.

- Bugfix: Entering date prefix but calling [count]-modified command crashes.
  [|dob-viewer|_]

- Bugfix: Applying meaningless delta-time still marks Fact dirty nonetheless.
  [|dob-viewer|_]

  - E.g., if Fact is 30 minutes wide, and you ``+30<TAB>`` to set end to
    30 minutes past start, Fact Diff would show no change, but on quit,
    dob would ask you to save.

- Bugfix: Rift jumpers change to first/final real Fact, not gap Fact.
  [|dob-viewer|_]

- UX: Swap ``G``/``gg`` and ``f``/``F`` command mappings.
  [|dob-viewer|_]

- Improve?: Update active gap Fact status on the tick.
  [|dob-viewer|_]

  - Updates X.XX in the text, "Gap Fact of X.XX mins. [edit to add]."

  - Except change the precision to one, e.g., X.X mins, so it updates
    less frequently. Otherwise, if hundredths place showing, the status
    message and the Fact Diff end time (which shows <now>) update at
    slightly different rates, but similar enough that it looks weird.

3.0.6 (2020-04-14)
==================

- Bugfix: Crash handling clock time parse error.
  [|dob-viewer|_]

  - Usually specifying clock time is okay, e.g., '100' is interpreted
    as 1:00a. But the hour and minute components were not being
    bounds-checked, i.e., 0..59. So, e.g., trying to decode '090'
    would crash (rather than be reported as not-a-date).

- Bugfix: Editor command handlers using stale "now".
  [|dob-viewer|_]

  - So, e.g., if you started dob at 5p, and now it's 6p, and the current
    Fact is active (no end time), pressing 'J' to jump back a day would
    find Fact from yesterday at 5p, not 6p. (I'm sure there were more
    important use cases where this was more harmful, but this is the
    most obvious one to highlight.)

- Bugfix: Relative edit time feature broken/shadowed by delta-time bindings.
  [|dob-viewer|_]

  - E.g., trying to type a relative time, say '+60', in the edit time widget
    was been intercepted by the newish delta-time feature. Consequently, the
    delta-time feature is now disabled when editing the start or end time.

- Bugfix: Commando save (``:w``) hides status message ('Saved {} Facts').
  [|dob-viewer|_]

- Feature: Jump to date (using ``G`` or ``gg`` command modifier prefix).
  [|dob-viewer|_]

  - E.g., ``20200410G`` will jump to first Fact on 2020-04-10.

  - User can specify (via config) allowable punctuation.

    - E.g., in addition to ``20200101G`` to jump to New Year's day, user
      can instead type ``2020-01-01G``, or ``2020/01/01G``, etc., depending
      on what ``date_separators`` are specified in the config.

  - More examples: ``100G`` jumps to Fact at 1:00 AM today.

    Or type ``2020/01/01 1400G`` or more simply ``2020010114G``
    to jump to 2p on New Year's day, 2020.

- Feature: Wire backspace to command modifier, commando, and time-delta modes.
  [|dob-viewer|_]

  - Pressing backspace will (naturally) remove the last character typed
    from the command modifier/commando/time-delta being built, or it'll
    cancel the operation if nothing is left to remove.

- Feature: Add true first/final Fact jump commands.
  [|dob-viewer|_]

  - Because ``G`` and ``gg`` stop on FactsManager group boundaries
    (these are the contiguous Fact "windows" the editor uses to
    store Facts in memory (which allows editing multiple Facts
    between database writes), and are used during the import process,
    which is really where stopping on group boundaries makes the most
    sense. In other words, we should probably make these commands the
    new ``G``/``gg``, and move the old commands to other key mappings.
    But I'm not ready to make that... leap).

  - The new commands are wired to ``f`` (final) and ``F`` (first) Fact jump.

- Improve: Show command modifier or delta-time in status as user types.
  [|dob-viewer|_]

  - Might as well, because we already display the commando as it's built.
    And it provides context to the user, which could be a teachable moment,
    if the user is learning by mashing (keys).

- Improve: Support allow-gap toggling.
  [|dob-viewer|_]

  - Now that the command modifier or time-delta is shown as a status
    message, it'll be obvious to the user if allow-gap is on or off.
    So pressing ``!!`` will first enable allow-gap, then disable it,
    rather than canceling the operation.

- Improve: Let user allow-gap (e.g., ``!``) before time-delta (``-``/``+``).
  [|dob-viewer|_]

  - E.g., in addition to ``+10!<ENTER>``, ``!+10<ENTER>`` also now works.

- Improve: Wire Ctrl-C to clear or cancel command modifier/commando/delta-time.
  [|dob-viewer|_]

- Improve: Allow Tab, in addition to Enter, to finish delta-time command.
  [|dob-viewer|_]

  - Because Tab is the left hand's Enter.

- Improve: Make easy to set end to "now" on active Fact (e.g., via ``[`` or ``]``).
  [|dob-viewer|_]

  - For active Fact, rather than the 1-minute decrement (``[``) and increment
    (``]``) operators using (now - 60 seconds) or (now + 60 seconds), just use
    now. (So if user wants to really remove 1 minute from now they can just
    press the key twice, e.g., ``[[``, or use a count modifier, e.g., ``1[``.)

- Improve: Linger to show 'Saved' message on save-and-exit commando (``:wq``).
  [|dob-viewer|_]

- Improve: Pass carousel-active indicator to post processors.
  [|dob-viewer|_]

  - So that plugins may behave differently when triggered by a save when dob
    is also quitting, versus a save from the interactive editor.

    - This is mostly useful so that a plugin does not errantly output any
      text to the display, which would mess up the editor interface.

- Improve: Add "from" to Jump Fact time reference status message, for context.
  [|dob-viewer|_]

3.0.5 (2020-04-13)
==================

- Improve: Alias command ``env`` to ``environs``.

  - E.g., ``dob env``.

- Feature: Make all key bindings user configurable.
  [|dob-viewer|_]

  - Run ``dob config dump editor-keys`` to see all the mappings.

  - User can specify zero, one, or multiple keys for each action.

- Improve: Remove 'escape'-only binding to avoid exit on unmapped Ctrl-keys.
  [|dob-viewer|_]

- Bugfix: Catch Ctrl-C on dirty-quit confirmation, to avoid unseemly stack trace.
  [|dob-viewer|_]

- Bugfix: Ctrl-W not saving on exit.
  [|dob-viewer|_]

- Improve: Remove the Ctrl-W save-and-exit key binding.
  [|dob-viewer|_]

  - Convention is that Ctrl-W is "close", but what would that be in dob?

  - The command remains but the binding was removed. The user can assign
    a key binding in their config if they want to enable this command.

- Feature: Vim-like command mode (lite).
  [|dob-viewer|_]

  - Just the three commands, ``:w``, ``:q``, and ``:wq``.

  - Because dob uses EDITOR, if Vim is user's editor, user could
    run ``:wq`` twice in a row to save their Fact description, leave
    the Vim editor, and then save and quit dob.

- Feature: Add modifier key (defaults to ``!``) to allow interval gap.
  [|dob-viewer|_]

  - E.g., consider the  command ``-1h``, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., ``-1!h``.

  - User can change the modifier key via the ``editor-keys.allow_time_gap``
    config setting.

- Feature: Add time command modifier (``!``) to allow interval gap.
  [|dob-viewer|_]

  - E.g., consider the  command ``-1h``, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., ``-1!h``.

- Feature: Convenient 1- and 5-minute single-key time nudging commands.
  [|dob-viewer|_]

  - E.g., ``[`` and ``]`` to decrement or increment end by 1 min., or
    add shift press for 5 mins., i.e., ``{`` and ``}``.

  - Likewise, use ``,`` and ``.`` to nudge start time
    backwards or forwards by 1 minute, respectively;
    and use ``<`` and ``>`` for five minutes instead.

  - All four keys are user-customizable, of course!

- Bugfix: Ensure Facts marked dirty after time nudging.
  [|dob-viewer|_]

  - Or user is not asked to save on exit after nudging time.

- Bugfix: Long press time nudge is not increasing deltas over time.
  [|dob-viewer|_]

  - E.g., if user holds Ctrl-left down, it starts adjusting the time by
    one minute for each press generated, but it was not increasing to
    five minutes per press, etc., the longer the user kept the key pressed.

- Improve: Ensure neighbor Fact time width not squashed to 0.
  [|dob-viewer|_]

- Bugfix: Cannot jump to first/final fact if current Fact within jump delta.
  [|dob-viewer|_]

  - E.g., Consider user is on current Fact, 2020-04-12 12:00 to 13:00, and
    the final Fact is from 2020-04-12 15:00 to 16:00. Pressing ``K`` does not
    jump to the final Fact, because it was less than 1 day ahead of current.

- Improve: On jump day from active Fact, use now as reference time.
  [|dob-viewer|_]

  - This feels more natural, rather than jumping from the start of the
    active Fact, and prevents jumping back more than a day.

- Feature: Add Vim-like [count] prefix to Jump and Nudge commands.
  [|dob-viewer|_]

  - E.g., user has been able to press ``j`` to go to the previous Fact.
    Now they can press ``5j`` to go back 5 Facts.

  - Likewise for jumping by day, e.g., ``2.5K`` will jump forward 2.5 days.

  - Same for time nudging, ``Ctrl-left`` has been used for decrementing the
    end time by 1 minute. Now user can specify exact amount, e.g., to
    decrease the end time by 4.2 minutes, the user can type ``4.2<Ctrl-left>``.

  - User can type ``!`` before or after digits to signal that a time nudge
    command should leave a gap rather than stretching a neighbor's time,
    e.g., ``!1<Ctrl-right>`` and ``1!<Ctrl-right>`` are equivalent.

  - To give user better visibility into what's happening, the jump commands
    now print a status message indicating how many days or number of Facts
    were jumped. When jumping by day, the time reference used is also shown,
    which is helpful if there's a long Fact or Gap, so the user does not get
    confused when their jump does not appear to do anything (i.e., when
    time reference changes but locates the same Fact that was showing).

- Bugfix: Prompt crashes if user presses Ctrl-D on empty text.
  [|dob-prompt|_]

- Bugfix: Prompt not positioned correctly after Escape keypress.
  [|dob-prompt|_]

- Enhance: Reset chosen completer on Ctrl-C (e.g., like pressing ``F2``).
  [|dob-prompt|_]

- API: Pass Click content to post_processor handler.
  [|dob-bright|_]

3.0.4 (2020-04-10)
==================

- Bugfix: ``config dump -T texttable`` broken.

- Improve: Make ``texttable`` use full terminal width.

- Improve: Use ``texttable`` as ``config dump`` table default (better wrapping).

- Improve: Ensure plugins loaded for ``config`` commands.

- Enhance: Reload config after plugins loaded, to load plugin config.

- Bugfix: ``dob config get`` with 2 or more parts stacktraces on unknown setting.

- Enhance: Let user clear end time of final Fact.
  [|dob-viewer|_]

- Bugfix: Set end time before start, and dob crashes after alert.
  [|dob-viewer|_]

- Improve: Use fact_min_delta as min. width on neighbor time adjust.
  [|dob-viewer|_]

- Improve: Allow config to be reloaded, to support plugin config.
  [|dob-bright|_]

- Bugfix: Interactive editor ``gg`` (jump to first Fact) fails.
  [|nark|_]

- Bugfix: Allow Unicode characters in config values.
  [|dob-bright|_]

3.0.3 (2020-04-08)
==================

- Deps: Update versions to profit from library bug fixes.

- Docs: Update contributing getting-started, and more.

- Enhance: Pause briefly on plugin import error so user sees message.

- Enhance: Pass path to plugins on eval, so they can load local assets.

3.0.2 (2020-04-01)
==================

- Bugfix: Incorrect version information emitted.

3.0.1 (2020-04-01)
==================

- Bugfix: Downstream fix repairs demo command (which was breaking
  because spaces in tags were not being converted properly to magic
  class names, causing PTK to explode, and then dob to ask something
  strange about okay-to-save).

- Improve: Simplify version report for non-devs.

- Docs: Runtime help fixes.

- DX: Fix Travis-CI not-POSIX issue.

3.0.0 (2020-03-30)
==================

- Split prompt and carousel/editor interfaces to separate projects,
  |dob-prompt|_ and |dob-viewer|_, respectively; and a shared
  project, |dob-bright|_.

  - This not only helps keep most of the Click CLI code separate from
    the PPT interface code, but it removes all of the recent front end
    work from the original |hamster-cli|_ codebase.

    - This comes at the expense of making developer onboarding a little
      more of a chore, because there are that many more repositories to
      clone. So perhaps now is a good time to plug a multiple-repository
      manager -- check out |ohmyrepos|_ to help you monitor all the
      projects that make up dob.

3.0.0a34 (2019-02-24)
=====================

- Hamster Renascence: Total Metempsychosis.

- New ``dob edit`` command, a colorful, interactive, terminal-based editor,
  i.e., Carousel Fact editor (though not *quite* a carousel, it doesn't wrap
  from beginning back to end, more of a conveyor belt, but that doesn't have
  quite the same image as a photo slideshow carousel).

- Sped up load time for quicker factoid entering #profiling
  (but who cares now that ``dob edit`` ).

- Learn dob quickly with the new ``dob demo`` feature.

- Modernized packaging infrastructure. Moved metadata to ``setup.cfg`` and
  dumped ``bumpversion`` for git-tags-aware ``setuptools_scm`` versioning.

- Setup HotOffThe Hamster CI accounts on Codecov, Travis CI, and ReadTheDocs.

- Attached Code of Conduct to Developer Contract.

3.0.0.beta.1 (2018-06-09)
=========================

- Add Natural language support, e.g., ``dob from 10 min ago to now ...``.

  - NOTE: For the new commands, the start and optional end times are now
    specified at the beginning of a new fact command, rather than after the
    fact (like in legacy ``hamster``).

- New database migration commands, e.g., ``migrate up``.

- Legacy DB support (i.e., upgrade script).

- Bulk ``import``, with conflict resolution, and ``export``.

- Interactive prompting! Powerful, wonderful UI to specify
  activity@category, and tags. With sorting and filtering.
  Just ``--ask``.

- Usage-aware ``TAB``-complete suggestions (e.g., most used
  tags, tags used recently, and more).

- New ``usage`` commands to show activity and tag usage counts,
  and cumulative durations.

- Easy, fast Fact ``edit``-ing.

- Refactor code, mostly breaking big files and long functions.

- Seriously lacking test coverage. =( But it's summertime now
  and I want to go run around outside. -lb

- Enhanced ``edit`` command.

View the :doc:`hamster-cli History <history-hamster-cli>` (pre-fork, pre-|dob|_).

