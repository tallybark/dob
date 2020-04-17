#######
History
#######

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |dob-bright| replace:: ``dob-bright``
.. _dob-bright: https://github.com/hotoffthehamster/dob-bright

.. |dob-prompt| replace:: ``dob-prompt``
.. _dob-prompt: https://github.com/hotoffthehamster/dob-prompt

.. |dob-viewer| replace:: ``dob-viewer``
.. _dob-viewer: https://github.com/hotoffthehamster/dob-viewer

.. |hamster-cli| replace:: ``hamster-cli``
.. _hamster-cli: https://github.com/projecthamster/hamster-cli

.. |ohmyrepos| replace:: OhMyRepos
.. _ohmyrepos: https://github.com/landonb/ohmyrepos

.. :changelog:

3.0.8 (2020-04-17)
===================

- Docs: Document the interactive editor.

- Improve: Remove requirement that custom paste config be numbered sequentially.
  [dob-viewer]

3.0.7 (2020-04-16)
==================

- Feature: Let user define custom key bindings for pasting arbitrary factoids.
  [dob-viewer]

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
  [dob-viewer]

  - One command to copy the current Fact meta and paste to the final Fact.

    - Currently mapped to ``Ctrl-e``.

  - One command to copy the current Fact meta, stop the final Fact,
    and paste to the new active Fact.

    - Currently mapped to ``V``.

  - One command to stop the final Fact, switch to the new active Fact,
    and prompt for the act\@gory.

    - Currently mapped to ``o``.

- Bugfix: Entering date prefix but calling [count]-modified command crashes.
  [dob-viewer]

- Bugfix: Applying meaningless delta-time still marks Fact dirty nonetheless.
  [dob-viewer]

  - E.g., if Fact is 30 minutes wide, and you ``+30<TAB>`` to set end to
    30 minutes past start, Fact Diff would show no change, but on quit,
    dob would ask you to save.

- Bugfix: Rift jumpers change to first/final real Fact, not gap Fact.
  [dob-viewer]

- UX: Swap ``G``/``gg`` and ``f``/``F`` command mappings.
  [dob-viewer]

- Improve?: Update active gap Fact status on the tick.
  [dob-viewer]

  - Updates X.XX in the text, "Gap Fact of X.XX mins. [edit to add]."

  - Except change the precision to one, e.g., X.X mins, so it updates
    less frequently. Otherwise, if hundredths place showing, the status
    message and the Fact Diff end time (which shows <now>) update at
    slightly different rates, but similar enough that it looks weird.

3.0.6 (2020-04-14)
==================

- Bugfix: Crash handling clock time parse error.
  [dob-viewer]

  - Usually specifying clock time is okay, e.g., '100' is interpreted
    as 1:00a. But the hour and minute components were not being
    bounds-checked, i.e., 0..59. So, e.g., trying to decode '090'
    would crash (rather than be reported as not-a-date).

- Bugfix: Editor command handlers using stale "now".
  [dob-viewer]

  - So, e.g., if you started dob at 5p, and now it's 6p, and the current
    Fact is active (no end time), pressing 'J' to jump back a day would
    find Fact from yesterday at 5p, not 6p. (I'm sure there were more
    important use cases where this was more harmful, but this is the
    most obvious one to highlight.)

- Bugfix: Relative edit time feature broken/shadowed by delta-time bindings.
  [dob-viewer]

  - E.g., trying to type a relative time, say '+60', in the edit time widget
    was been intercepted by the newish delta-time feature. Consequently, the
    delta-time feature is now disabled when editing the start or end time.

- Bugfix: Commando save (``:w``) hides status message ('Saved {} Facts').
  [dob-viewer]

- Feature: Jump to date (using ``G`` or ``gg`` command modifier prefix).
  [dob-viewer]

  - E.g., ``20200410G`` will jump to first Fact on 2020-04-10.

  - User can specify (via config) allowable punctuation.

    - E.g., in addition to ``20200101G`` to jump to New Year's day, user
      can instead type ``2020-01-01G``, or ``2020/01/01G``, etc., depending
      on what ``date_separators`` are specified in the config.

  - More examples: ``100G`` jumps to Fact at 1:00 AM today.

    Or type ``2020/01/01 1400G`` or more simply ``2020010114G``
    to jump to 2p on New Year's day, 2020.

- Feature: Wire backspace to command modifier, commando, and time-delta modes.
  [dob-viewer]

  - Pressing backspace will (naturally) remove the last character typed
    from the command modifier/commando/time-delta being built, or it'll
    cancel the operation if nothing is left to remove.

- Feature: Add true first/final Fact jump commands.
  [dob-viewer]

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
  [dob-viewer]

  - Might as well, because we already display the commando as it's built.
    And it provides context to the user, which could be a teachable moment,
    if the user is learning by mashing (keys).

- Improve: Support allow-gap toggling.
  [dob-viewer]

  - Now that the command modifier or time-delta is shown as a status
    message, it'll be obvious to the user if allow-gap is on or off.
    So pressing ``!!`` will first enable allow-gap, then disable it,
    rather than canceling the operation.

- Improve: Let user allow-gap (e.g., ``!``) before time-delta (``-``/``+``).
  [dob-viewer]

  - E.g., in addition to ``+10!<ENTER>``, ``!+10<ENTER>`` also now works.

- Improve: Wire Ctrl-C to clear or cancel command modifier/commando/delta-time.
  [dob-viewer]

- Improve: Allow Tab, in addition to Enter, to finish delta-time command.
  [dob-viewer]

  - Because Tab is the left hand's Enter.

- Improve: Make easy to set end to "now" on active Fact (e.g., via ``[`` or ``]``).
  [dob-viewer]

  - For active Fact, rather than the 1-minute decrement (``[``) and increment
    (``]``) operators using (now - 60 seconds) or (now + 60 seconds), just use
    now. (So if user wants to really remove 1 minute from now they can just
    press the key twice, e.g., ``[[``, or use a count modifier, e.g., ``1[``.)

- Improve: Linger to show 'Saved' message on save-and-exit commando (``:wq``).
  [dob-viewer]

- Improve: Pass carousel-active indicator to post processors.
  [dob-viewer]

  - So that plugins may behave differently when triggered by a save when dob
    is also quitting, versus a save from the interactive editor.

    - This is mostly useful so that a plugin does not errantly output any
      text to the display, which would mess up the editor interface.

- Improve: Add "from" to Jump Fact time reference status message, for context.
  [dob-viewer]

3.0.5 (2020-04-13)
==================

- Improve: Alias command ``env`` to ``environs``.

  - E.g., ``dob env``.

- Feature: Make all key bindings user configurable. [dob-viewer]

  - Run ``dob config dump editor-keys`` to see all the mappings.

  - User can specify zero, one, or multiple keys for each action.

- Improve: Remove 'escape'-only binding to avoid exit on unmapped Ctrl-keys. [dob-viewer]

- Bugfix: Catch Ctrl-C on dirty-quit confirmation, to avoid unseemly stack trace.
  [dob-viewer]

- Bugfix: Ctrl-W not saving on exit. [dob-viewer]

- Improve: Remove the Ctrl-W save-and-exit key binding. [dob-viewer]

  - Convention is that Ctrl-W is "close", but what would that be in dob?

  - The command remains but the binding was removed. The user can assign
    a key binding in their config if they want to enable this command.

- Feature: Vim-like command mode (lite). [dob-viewer]

  - Just the three commands, ``:w``, ``:q``, and ``:wq``.

  - Because dob uses EDITOR, if Vim is user's editor, user could
    run ``:wq`` twice in a row to save their Fact description, leave
    the Vim editor, and then save and quit dob.

- Feature: Add modifier key (defaults to ``!``) to allow interval gap. [dob-viewer]

  - E.g., consider the  command ``-1h``, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., ``-1!h``.

  - User can change the modifier key via the ``editor-keys.allow_time_gap``
    config setting.

- Feature: Add time command modifier (``!``) to allow interval gap. [dob-viewer]

  - E.g., consider the  command ``-1h``, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., ``-1!h``.

- Feature: Convenient 1- and 5-minute single-key time nudging commands. [dob-viewer]

  - E.g., ``[`` and ``]`` to decrement or increment end by 1 min., or
    add shift press for 5 mins., i.e., ``{`` and ``}``.

  - Likewise, use ``,`` and ``.`` to nudge start time
    backwards or forwards by 1 minute, respectively;
    and use ``<`` and ``>`` for five minutes instead.

  - All four keys are user-customizable, of course!

- Bugfix: Ensure Facts marked dirty after time nudging. [dob-viewer]

  - Or user is not asked to save on exit after nudging time.

- Bugfix: Long press time nudge is not increasing deltas over time. [dob-viewer]

  - E.g., if user holds Ctrl-left down, it starts adjusting the time by
    one minute for each press generated, but it was not increasing to
    five minutes per press, etc., the longer the user kept the key pressed.

- Improve: Ensure neighbor Fact time width not squashed to 0. [dob-viewer]

- Bugfix: Cannot jump to first/final fact if current Fact within jump delta. [dob-viewer]

  - E.g., Consider user is on current Fact, 2020-04-12 12:00 to 13:00, and
    the final Fact is from 2020-04-12 15:00 to 16:00. Pressing ``K`` does not
    jump to the final Fact, because it was less than 1 day ahead of current.

- Improve: On jump day from active Fact, use now as reference time. [dob-viewer]

  - This feels more natural, rather than jumping from the start of the
    active Fact, and prevents jumping back more than a day.

- Feature: Add Vim-like [count] prefix to Jump and Nudge commands. [dob-viewer]

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

- Bugfix: Prompt crashes if user presses Ctrl-D on empty text. [dob-prompt]

- Bugfix: Prompt not positioned correctly after Escape keypress. [dob-prompt]

- Enhance: Reset chosen completer on Ctrl-C (e.g., like pressing ``F2``). [dob-prompt]

- API: Pass Click content to post_processor handler. [dob-bright]

3.0.4 (2020-04-10)
==================

- Bugfix: ``config dump -T texttable`` broken.

- Improve: Make ``texttable`` use full terminal width.

- Improve: Use ``texttable`` as ``config dump`` table default (better wrapping).

- Improve: Ensure plugins loaded for ``config`` commands.

- Enhance: Reload config after plugins loaded, to load plugin config.

- Bugfix: ``dob config get`` with 2 or more parts stacktraces on unknown setting.

- Enhance: Let user clear end time of final Fact. [dob-viewer]

- Bugfix: Set end time before start, and dob crashes after alert. [dob-viewer]

- Improve: Use fact_min_delta as min. width on neighbor time adjust. [dob-viewer]

- Improve: Allow config to be reloaded, to support plugin config. [dob-bright]

- Bugfix: Interactive editor ``gg`` (jump to first Fact) fails. [nark]

- Bugfix: Allow Unicode characters in config values. [dob-bright]

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

