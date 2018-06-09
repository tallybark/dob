.. :changelog:

History
-------

3.0.0.beta.1 (2018-06-09)
-------------------------
FIXME: move some of these to the LIB...
* Parser rewrite. More regex. Offload datetime parsing to iso8601.
* Add Natural language support, e.g., ``dob from 10 min ago to now ...``.
  NOTE: For the new commands, the start and optional end times are now
  specified at the beginning of a new fact command, rather than after the
  fact. (There's still a command that supports the Legacy Hamster CLI format,
  where the start and end times follow the fact description).
* New database migration commands, e.g., ``migrate up``.
* Legacy DB support (i.e., upgrade script).
* Bulk ``import``, with conflict resolution, and ``export``.
* Interactive prompting! Powerful, wonderful UI to specify
  activity@category, and tags. With sorting and filtering.
  Just ``--ask``.
* Usage-aware ``TAB``-complete suggestions (e.g., most used
  tags, tags used recently, and more).
* New ``usage`` commands to show activity and tag usage counts,
  and cumulative durations.
* Easy, fast Fact ``edit``-ing.
* Refactor code, mostly breaking big files and long functions.
* Seriously lacking test coverage. =( But it's summertime now
  and I want to go run around outside. -lb
* Enhanced ``edit`` command.

0.12.0 (2016-04-25)
-------------------
* ``stop`` now shows detail on the fact saved.
* ``current`` now shows how much time was accumulated so far.
* Remove standalone script block. You are expected to utilize pip/setuptools to
  setup ``hamster_cli``. ``virtualenvs`` FTW!
* Testenvironment now uses linkchecks and ``doc8`` for validating the
  documentation.
* Removed 'GTK window' related pseudo methods. Until the functionality is
  actually here.
* Added ``manifest`` validation to testenvironment.
* Added ``pep257`` validation to testsuite.
* Vastly improved docstring, docstringcoverage and frontend helptexts.
* Use ``hamsterlib 0.10.0`` new improved config layout.
* Add GPL boilerplate and frontend information.
* ``release`` make target now uses ``twine``.
* Provide new ``details`` command to list basic runtime environment details.

0.11.0 (2016-04-16)
--------------------
* New, solid config handling.
* Switch to `semantic versioning <http://semver.org>`_.
* Move CI from codeship to Travis-CI.
* First batch of very basic integration tests.
* Several fixes to packaging.

0.1.0 (2016-04-09)
---------------------
* First release on PyPI.
* Prove-of-concept release.
* Most of the basic functionality is there.
* Provides basic test coverage.
