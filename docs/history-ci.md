# History

[comment]: # DEV: release-ghub-pypi scrapes Markdown from the first section below for the GitHub release.

[dob]: https://github.com/hotoffthehamster/dob
    "`dob`"

[hamster-cli History]: ./history-hamster-cli
    "hamster-cli History"

## 3.0.0rc1 (2020-01-27)

[dob-prompt]: https://github.com/hotoffthehamster/dob-prompt
    "`dob-prompt`"

[dob-viewer]: https://github.com/hotoffthehamster/dob-viewer
    "`dob-viewer`"

* Split prompt and carousel/editor interfaces to separate projects,
  [dob-prompt][] and [dob-viewer][], respectively.

* A year's worth of development, minus an extended holiday. Enjoy!

## 3.0.0a34 (2019-02-24)

* Hamster Renascence: Total Metempsychosis.

* New `dob edit` command, a colorful, interactive, terminal-based editor,
  i.e., Carousel Fact editor (though not *quite* a carousel, it doesn't wrap
  from beginning back to end, more of a conveyor belt, but that doesn't have
  quite the same image as a photo slideshow carousel).

* Sped up load time for quicker factoid entering #profiling
  (but who cares now that `dob edit` ).

* Learn dob quickly with the new `dob demo` feature.

* Modernized packaging infrastructure. Moved metadata to `setup.cfg` and
  dumped `bumpversion` for git-tags-aware `setuptools_scm` versioning.

* Setup HotOffThe Hamster CI accounts on Codecov, Travis CI, and ReadTheDocs.

* Attached Code of Conduct to Developer Contract.

## 3.0.0.beta.1 (2018-06-09)

* Add Natural language support, e.g., `dob from 10 min ago to now ...`.
  NOTE: For the new commands, the start and optional end times are now
  specified at the beginning of a new fact command, rather than after the
  fact.

* New database migration commands, e.g., `migrate up`.

* Legacy DB support (i.e., upgrade script).

* Bulk `import`, with conflict resolution, and `export`.

* Interactive prompting! Powerful, wonderful UI to specify
  activity@category, and tags. With sorting and filtering.
  Just `--ask`.

* Usage-aware `TAB`-complete suggestions (e.g., most used
  tags, tags used recently, and more).

* New `usage` commands to show activity and tag usage counts,
  and cumulative durations.

* Easy, fast Fact `edit`-ing.

* Refactor code, mostly breaking big files and long functions.

* Seriously lacking test coverage. =( But it's summertime now
  and I want to go run around outside. -lb

* Enhanced `edit` command.

View the [hamster-cli History][] (pre-fork, pre-[dob][]).

