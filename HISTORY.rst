#######
History
#######

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |hamster-cli| replace:: ``hamster-cli``
.. _hamster-cli: https://github.com/projecthamster/hamster-cli

.. :changelog:

3.0.0a31 (2019-02-21)
=====================

- Hamster Renascence: Total Metempsychosis.

3.0.0.beta.1 (2018-06-09)
=========================

* Add Natural language support, e.g., ``dob from 10 min ago to now ...``.
  NOTE: For the new commands, the start and optional end times are now
  specified at the beginning of a new fact command, rather than after the
  fact.
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

View the :doc:`hamster-cli History <history-hamster-cli>` (pre-fork, pre-|dob|_).

