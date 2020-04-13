# History

[comment]: # DEV: release-ghub-pypi scrapes Markdown from the first section below for the GitHub release.

[hamster-cli]: https://github.com/projecthamster/hamster-cli
    "`hamster-cli`"

[hamster-cli History]: https://github.com/projecthamster/hamster-cli/blob/develop/HISTORY.rst
    "hamster-cli History"

[OhMyRepos]: https://github.com/landonb/ohmyrepos
    "OhMyRepos"

## 3.0.5 (2020-04-13)

[dob]: https://github.com/hotoffthehamster/dob
    "`dob`"

[nark]: https://github.com/hotoffthehamster/nark
    "`nark`"

[dob-bright]: https://github.com/hotoffthehamster/dob-bright
    "`dob-bright`"

[dob-prompt]: https://github.com/hotoffthehamster/dob-prompt
    "`dob-prompt`"

[dob-viewer]: https://github.com/hotoffthehamster/dob-viewer
    "`dob-viewer`"

- Improve: Alias command `env` to `environs`. [[dob][]]

  - E.g., `dob env`.

- Feature: Make all key bindings user configurable. [[dob-viewer][]]

  - Run `dob config dump editor-keys` to see all the mappings.

  - User can specify zero, one, or multiple keys for each action.

- Improve: Remove 'escape'-only binding to avoid exit on unmapped Ctrl-keys. [[dob-viewer][]]

- Bugfix: Catch Ctrl-C on dirty-quit confirmation, to avoid unseemly stack trace. [[dob-viewer][]]

- Bugfix: Ctrl-W not saving on exit. [[dob-viewer][]]

- Improve: Remove the Ctrl-W save-and-exit key binding. [[dob-viewer][]]

  - Convention is that Ctrl-W is "close", but what would that be in dob?

  - The command remains but the binding was removed. The user can assign
    a key binding in their config if they want to enable this command.

- Feature: Vim-like command mode (lite). [[dob-viewer][]]

  - Just the three commands, `:w`, `:q`, and `:wq`.

  - Because dob uses EDITOR, if Vim is user's editor, user could
    run `:wq` twice in a row to save their Fact description, leave
    the Vim editor, and then save and quit dob.

- Feature: +/-N time adjustment commands. [[dob-viewer][]]

  - Type minus to begin a start time adjustment command. E.g., if you
    want to set the start time to ten minutes before the end time, type
    `-10<CR>`. Or type `-10m` (for minutes). For the active Fact, the
    time is calculated relative to "now".

  - Type a plus to begin an end time adjustment command, followed by
    an integer or floating point number, and then press Enter or "m"
    for minutes, or "h" for hours.

    - E.g., to set the end time 2.5 hours after the start time, type `+2.5h`.

- Feature: Add modifier key (defaults to `!`) to allow interval gap. [[dob-viewer][]]

  - E.g., consider the  command `-1h`, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., `-1!h`.

  - User can change the modifier key via the `editor-keys.allow_time_gap`
    config setting.

- Feature: Convenient 1- and 5-minute single-key time nudging commands. [[dob-viewer][]]

  - E.g., `[` and `]` to decrement or increment end by 1 min., or
    add shift press for 5 mins., i.e., `{` and `}`.

  - Likewise, use `,` and `.` to nudge start time
    backwards or forwards by 1 minute, respectively;
    and use `<` and `>` for five minutes instead.

  - All four keys are user-customizable, of course!

- Bugfix: Ensure Facts marked dirty after time nudging. [[dob-viewer][]]

  - Or user is not asked to save on exit after nudging time.

- Bugfix: Long press time nudge is not increasing deltas over time. [[dob-viewer][]]

  - E.g., if user holds Ctrl-left down, it starts adjusting the time by
    one minute for each press generated, but it was not increasing to
    five minutes per press, etc., the longer the user kept the key pressed.

- Improve: Ensure neighbor Fact time width not squashed to 0. [[dob-viewer][]]

- Bugfix: Cannot jump to first/final fact if current Fact within jump delta. [[dob-viewer][]]

  - E.g., Consider user is on current Fact, 2020-04-12 12:00 to 13:00, and
    the final Fact is from 2020-04-12 15:00 to 16:00. Pressing `K` does not
    jump to the final Fact, because it was less than 1 day ahead of current.

- Improve: On jump day from active Fact, use now as reference time. [[dob-viewer][]]

  - This feels more natural, rather than jumping from the start of the
    active Fact, and prevents jumping back more than a day.

- Feature: Add Vim-like [count] prefix to Jump and Nudge commands. [[dob-viewer][]]

  - E.g., user has been able to press `j` to go to the previous Fact.
    Now they can press `5j` to go back 5 Facts.

  - Likewise for jumping by day, e.g., `2.5K` will jump forward 2.5 days.

  - Same for time nudging, `Ctrl-left` has been used for decrementing the
    end time by 1 minute. Now user can specify exact amount, e.g., to
    decrease the end time by 4.2 minutes, the user can type `4.2<Ctrl-left>`.

  - User can type `!` before or after digits to signal that a time nudge
    command should leave a gap rather than stretching a neighbor's time,
    e.g., `!1<Ctrl-right>` and `1!<Ctrl-right>` are equivalent.

  - To give user better visibility into what's happening, the jump commands
    now print a status message indicating how many days or number of Facts
    were jumped. When jumping by day, the time reference used is also shown,
    which is helpful if there's a long Fact or Gap, so the user does not get
    confused when their jump does not appear to do anything (i.e., when
    time reference changes but locates the same Fact that was showing).

- Bugfix: Prompt crashes if user presses Ctrl-D on empty text. [[dob-prompt][]]

- Bugfix: Prompt not positioned correctly after Escape keypress. [[dob-prompt][]]

- Enhance: Reset chosen completer on Ctrl-C (e.g., like pressing ``F2``). [[dob-prompt][]]

- API: Pass Click content to post_processor handler. [[dob-bright][]]

## 3.0.4 (2020-04-10)

- Bugfix: `config dump -T texttable` broken. [[dob][]]

- Improve: Make `texttable` use full terminal width. [[dob][]]

- Improve: Use `texttable` as `config dump` table default (better wrapping). [[dob][]]

- Improve: Ensure plugins loaded for `config` commands. [[dob][]]

- Enhance: Reload config after plugins loaded, to load plugin config. [[dob][]]

- Bugfix: `dob config get` with 2 or more parts stacktraces on unknown setting. [[dob][]]

- Enhance: Let user clear end time of final Fact. [[dob-viewer][]]

- Bugfix: Set end time before start, and dob crashes after alert. [[dob-viewer][]]

- Improve: Use fact_min_delta as min. width on neighbor time adjust. [[dob-viewer][]]

- Improve: Allow config to be reloaded, to support plugin config. [[dob-bright][]]

- Bugfix: Interactive editor `gg` (jump to first Fact) fails. [[nark][]]

- Bugfix: Allow Unicode characters in config values. [[dob-bright][]]

## 3.0.3 (2020-04-08)

- Deps: Update versions to profit from library bug fixes.

- Docs: Update contributing getting-started, and more.

- Enhance: Pause briefly on plugin import error so user sees message.

- Enhance: Pass path to plugins on eval, so they can load local assets.

## 3.0.2 (2020-04-01)

- Bugfix: Incorrect version information emitted.

## 3.0.1 (2020-04-01)

- Bugfix: Downstream fix repairs demo command (which was breaking
  because spaces in tags were not being converted properly to magic
  class names, causing PTK to explode, and then dob to ask something
  strange about okay-to-save).

- Improve: Simplify version report for non-devs.

- Docs: Runtime help fixes.

- DX: Fix Travis-CI not-POSIX issue.

## 3.0.0 (2020-03-30)

- Split prompt and carousel/editor interfaces to separate projects,
  [dob-prompt][] and [dob-viewer][], respectively; and a shared
  project, [dob-bright][].

  - This not only helps keep most of the Click CLI code separate from
    the PPT interface code, but it removes all of the recent front end
    work from the original hamster-cli codebase.

    - This comes at the expense of making developer onboarding a little
      more of a chore, because there are that many more repositories to
      clone. So perhaps now is a good time to plug a multiple-repository
      manager -- check out [OhMyRepos][] to help you monitor all the
      projects that make up dob.

## 3.0.0a34 (2019-02-24)

- Hamster Renascence: Total Metempsychosis.

- New `dob edit` command, a colorful, interactive, terminal-based editor,
  i.e., Carousel Fact editor (though not *quite* a carousel, it doesn't wrap
  from beginning back to end, more of a conveyor belt, but that doesn't have
  quite the same image as a photo slideshow carousel).

- Sped up load time for quicker factoid entering #profiling
  (but who cares now that `dob edit` ).

- Learn dob quickly with the new `dob demo` feature.

- Modernized packaging infrastructure. Moved metadata to `setup.cfg` and
  dumped `bumpversion` for git-tags-aware `setuptools_scm` versioning.

- Setup HotOffThe Hamster CI accounts on Codecov, Travis CI, and ReadTheDocs.

- Attached Code of Conduct to Developer Contract.

## 3.0.0.beta.1 (2018-06-09)

- Add Natural language support, e.g., `dob from 10 min ago to now ...`.
  NOTE: For the new commands, the start and optional end times are now
  specified at the beginning of a new fact command, rather than after the
  fact.

- New database migration commands, e.g., `migrate up`.

- Legacy DB support (i.e., upgrade script).

- Bulk `import`, with conflict resolution, and `export`.

- Interactive prompting! Powerful, wonderful UI to specify
  activity@category, and tags. With sorting and filtering.
  Just `--ask`.

- Usage-aware `TAB`-complete suggestions (e.g., most used
  tags, tags used recently, and more).

- New `usage` commands to show activity and tag usage counts,
  and cumulative durations.

- Easy, fast Fact `edit`-ing.

- Refactor code, mostly breaking big files and long functions.

- Seriously lacking test coverage. =( But it's summertime now
  and I want to go run around outside. -lb

- Enhanced `edit` command.

View the [hamster-cli History][] (pre-fork, pre-[dob][]).

