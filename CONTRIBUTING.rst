Contributing
============

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

.. |user-docs| replace:: user documentation
.. _user-docs: https://github.com/hotoffthehamster/dob/tree/master/docs

.. |envlist| replace:: ``envlist``
.. _envlist: https://tox.readthedocs.io/en/latest/config.html#conf-envlist

.. |flake8| replace:: ``flake8``
.. _flake8: http://flake8.pycqa.org/en/latest/

.. |isort| replace:: ``isort``
.. _isort: https://github.com/timothycrosley/isort

.. |pdb| replace:: ``pdb``
.. _pdb: https://docs.python.org/3/library/pdb.html

.. |pytest| replace:: ``pytest``
.. _pytest: https://docs.pytest.org/en/latest/

.. |tox| replace:: ``tox``
.. _tox: https://tox.readthedocs.io/en/latest/

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |virtualenvwrapper| replace:: ``virtualenvwrapper``
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/

.. |PEP-257| replace:: PEP 257
.. _PEP-257: https://www.python.org/dev/peps/pep-0257/

.. |goog-py-sty| replace:: Google Python Style Guide
.. _goog-py-sty: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings

.. contents:: Contributing Contents
   :depth: 2
   :local:

Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given (if so desired).

How to Contribute
-----------------

First, please respect the `Code of Conduct`__ and each other.

__ https://dob.readthedocs.io/en/latest/code-of-conduct.html

Then, decide how you'd like to contribute:

Report Bugs
^^^^^^^^^^^

Report bugs at https://github.com/hotoffthehamster/dob/issues.

When reporting a bug, please include:

* Your operating system name and version, and the Python version you are using.

* Any details about your local setup that might be helpful for troubleshooting.

* Detailed steps to reproduce the bug.

Fix Bugs
^^^^^^^^

Look through the GitHub issues for anything tagged with "bug".
Pick one, assign yourself to it, and work on the issue.

Implement Features
^^^^^^^^^^^^^^^^^^

Look through the GitHub issues for anything tagged with "feature".
Pick one, assign yourself to it, and work on the issue.

Write Documentation
^^^^^^^^^^^^^^^^^^^

If you find documentation out of date, missing, or confusing, please help
us to improve it.

This includes the official |user-docs|_,
the `README
<https://github.com/hotoffthehamster/dob/blob/master/README.rst>`__,
and the inline docstrings that generate the `API documentation
<https://dob.readthedocs.io/en/latest/modules.html>`__
(per |PEP-257|_ and |goog-py-sty|_).

We also appreciate reference from blog posts, articles, and other projects.

Submit Feedback
^^^^^^^^^^^^^^^

The best way to send feedback is to file an issue at
https://github.com/hotoffthehamster/dob/issues.

See above for reporting bugs.

If you are proposing a feature:

* Explain in detail how the feature should work.
* Unless you expect to work on the code yourself, your chances of having a
  feature implemented are greater if you keep the scope focused and narrow
  such that it's as simple as possible for a developer to work on.
  That, or a monetary contribution speaks volumes.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome! You are encouraged to fork the project, hack away, and submit
  pull requests for new features (and bug fixes).
* Above all else, please be considerate and kind.
  A few nice words can go a long way!

Please also feel free to email the author directly if you have any other
questions or concerns. Response times may vary depending on season.

Getting Started
---------------

Ready to contribute? Here's how to set up |dob|_
for local development.

#. Dob is (for better and for worse) split across a number of projects.
   Fork each of these projects on GitHub:

   * |dob|_

   * |dob-viewer|_

   * |dob-prompt|_

   * |dob-bright|_

   * |nark|_

#. Clone your forks locally.

   For instance, open a terminal, change to a directory you'd like to
   develop from, and then run the commands::

    GH_URL=git@github.com:<your_user>
    for repo in dob dob-viewer dob-prompt dob-bright nark; do
      git clone ${GH_URL}/${repo}.git
    done

#. Prepare a Python virtual instance, or |virtualenv|_.

   First, ensure that you have |virtualenvwrapper|_ installed.

#. Next, set up a virtual environment for local development. Assuming you're
   still in the base directory where you cloned all the projects, change into
   the ``dob/`` directory and make the virtual environment::

    $ cd dob/
    $ mkvirtualenv -a $(pwd) dob
    (dob) $

   *Note:* We use the ``-a`` option so that ``cdproject`` changes directories
   to the ``dob/`` directory when we're in the virtual
   environment.

   *Note:* You can also specify the version of Python if you wish, e.g.,
   add the option ``--python=/usr/bin/python3.8``.

#. Now, prepare a special requirements file so you can run *1* command to
   install all five projects, rather than having to run the same command
   *5* times from five different directories.

   Copy the example file included in the project and rename it.

   From the base ``dob/`` directory, run::

    (dob) $ cp requirements/ultra-editable.pip.example requirements/ultra-editable.pip

   If you're following the instructions here, you should not need to edit
   the new file. But you might want to peak inside the file anyway to see
   how it works.

#. Finally, we're ready to install dob for local development!

   From the base ``dob/`` directory, run::

    (dob) $ make develop

   And that's it!
   The make task will install dependencies from `PyPI <https://pypi.org/>`__,
   as well as all the projects you sourced locally.

   - *Hint:* As usual, run ``workon`` to activate the virtual environment, and
     ``deactivate`` to leave it. E.g.,::

       # Load the Python virtual instance.
       $ workon dob
       (dob) $

       # Do your work.
       (dob) $ ...

       # Finish up.
       (dob) $ deactivate
       $

#. Now that your local development environment is setup, you can do some real work!

   However, before starting any work on a new feature or bug fix, make sure your
   ``develop`` branch is up to date with the official branch::

    (dob) $ cdproject
    (dob) $ git remote add upstream git@github.com:hotoffthehamster/dob.git
    (dob) $ git fetch upstream
    (dob) $ git checkout develop
    (dob) $ git merge --ff-only upstream/develop
    (dob) $ git push origin HEAD  # For good measure.

   And also do the same for each of the other local projects.

   (If you're concerned that managing multiple repositories is a chore,
   you're right! Which is why I like to use
   `myrepos <https://myrepos.branchable.com/>`__
   and `Oh, My Repos! <https://github.com/landonb/ohmyrepos>`__
   to be able to run the same operation against multiple repositories
   using a single command.)

#. Now that you've updated your local code to the freshest upstream sources,
   create a branch for local development. If you are working on an known issue,
   you may want to reference the Issue number in the branch name, e.g.,::

    $ git checkout -b feature/ISSUE-123-name-of-your-issue

   In any case, create a new branch, and start editing code.

#. Do your work and make one or more sane, concise commits::

    $ git add -p
    $ git commit -m "<Category>: <Short description of changes.>

    - <Longer description, if necessary.>"

   IMPORTANT: Please make each commit as small and sane as possible.

   Follow these guidelines:

   * Each commit should generally focus on one thing, and one thing only,
     and that thing should be clearly described in the first line of the
     commit message.

   * Please use a one-word categorical prefix (see below) to make it easy for
     someone reading the git log to understand the breadth of your changes.

   * If you move or refactor code, the move or refactor should be captured
     in a single commit *with no other code changes.*

     E.g., if you want to enhance a function, but you find that you need to
     refactor it to make it easier to hack on, first refactor the function
     -- without adding any new code or making any other changes -- and then
     make a commit, using the ``Refactor:`` prefix. Next, add your new code,
     and then make a second commit for the new feature/enhancement.

   * Following are some examples of acceptable commit message prefixes:

     * ``Feature: Added new feature.``

     * ``Bugfix: Fixed problem doing something.``

     * ``Refactor: Split long function into many.``

     * ``Version: X.Y.Z.``

     * ``Tests: Did something to tests.``

     * ``Docs: Update developer README.``

     * ``Debug: Add trace messages.``

     * ``Developer: Improved developer experience [akin to `Debug:` prefix].``

     * ``Linting: Adjust whitespace.``

     * ``Regression: Oh, boy, when did this get broke?``

     * ``i18n/l10n: Something about words.``

     * ``Feedback: Fix something per PR feedback.``

     (You'll notice that this strategy is similar to
     `gitmoji <https://gitmoji.carloscuesta.me/>`__,
     but it's more concise, and less obtuse.)

#. Throughout development, run tests and the linter -- and definitely before
   you submit a Pull Request.

   |dob|_ uses
   |flake8|_ for linting,
   |pytest|_ for unit testing, and
   |tox|_ for verifying against the many versions of Python.

   You can run all of these tools with one command
   that should be familiar to seasoned Python developers::

     $ tox

   Or you can run the equivalent make task::

     $ make test-all

   (which simply executes |tox|_).

   .. _rebase_and_squash:

#. Rebase and squash your work, if necessary, before submitting a Pull Request.

   E.g., if the linter caught an error, rather than making a new commit
   with just the linting fix(es), make a temporary commit with the linting
   fixes, and then "fixup" that commit into the previous commit wherein
   you originally added the code that didn't lint.

   (*Note:* Rebasing is an intermediate Git skill.
   If you're unfamiliar, read up elsewhere.
   But consider a few reminders.
   First, ensure that you are not rebasing any branch that other developers
   are also working on (which should not apply to your feature branch, unless
   you are collaborating with others on that branch, which you are probably not).
   Second, remember that ``git rebase --abort`` can save you from having to
   resolve any unanticipated or complicated conflicts, should you find
   yourself faced with rebase conflicts and unsure how to get your work back
   (abort the rebase and maybe ask someone for help, and try another approach).)

   For example, pretend that I have the following git history::

    $ git log --oneline | head -3

    b1c07a4 Regression: Fix some old bug.
    17d1e38 Feature: Add my new feature.
    2e888c3 Bugfix: Oops! Did I do that?

   and then I commit a linting fix that should have been included with
   the second-to-last commit, ``17d1e38``.

   First, add the linting fix::

    $ git add -A

   Then, use the ``fixup`` feature to tell Git which commit this belongs in::

    $ git ci --fixup=17d1e38

   Next, start a rebase, and use ``--autosquash``::

    $ git rebase --autosquash -i 2e888c3

   (*Note:* Use the SHA1 hash of the commit *after* the first one you want
   to be included in the rebase.)

   Git should open your default editor with a file that look like this::

    pick 17d1e38 Feature: Add my new feature.
    fixup f05e080 fixup! Feature: Add my new feature.
    pick b1c07a4 Regression: Fix some old bug.

   You'll notice that Git already reordered the commits and set the commit
   in question to "fixup".

   You can just save and close the file and Git will complete the rebase.

   - This is just one example of rebasing, and a rather advanced one at
     that (I'm not sure how many people use ``--autosquash``, but I love
     it!).

     Please search online or ask for help if you find yourself struggling
     to understand and perform rebasing.

#. Push the changes to your GitHub account.

   After testing and linting, and double-checking that your new feature or
   bugfix works, and rebasing, and committing your changes, push them to
   the branch on your GitHub account::

    $ git push origin feature/ISSUE-123-name-of-your-issue

   *Note:* If you pushed your work previosuly and then rebased, you may
   have to force-push::

    $ git push origin feature/ISSUE-123-name-of-your-issue --force

   .. _rebase_atop_develop:

#. Finally,
   `submit a pull request
   <https://github.com/hotoffthehamster/dob/pulls>`_
   through the GitHub website.

   *Important:* Please rebase your code against ``develop`` and resolve
   merge conflicts, so that project maintainers does not have to do so
   themselves. E.g.,::

    $ git checkout feature/ISSUE-123-name-of-your-issue
    $ git fetch upstream
    $ git rebase upstream/develop
    # Resolve any conflicts...
    $ git push origin HEAD --force
    # And then open the Pull Request.

(*Ansible users:* You might enjoy this Dob-dev setup role:
https://github.com/landonb/zoidy_dob-dev.)

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. Update docs.

   * Use docstrings to document new functions, and use (hopefully concise)
     inline comments as appropriate.

     * Follow the conventions defined by |PEP-257|_ and |goog-py-sty|_.

   * Document broader concepts and capture API changes and additions
     in the |user-docs|_.

2. Include tests.

   * If a pull request adds new classes or methods, they should be tested,
     either implicitly, because they're already called by an existing test.
     Or they should be tested explicitly, because you added new tests for them.

   * We strive for test coverage in the high-90s (it's too tedious to hit
     all branches and get 100%), but we do not enforce it.
     Please provide tests that provide majority coverage of your new code
     (you can ignore or consider error handling branches less important to
     cover, but all branches would still be good to test!).

     * Note that, as of early 2020, existing test coverage is no where near
       100%, so take this guideline with a grain of salt. If existing code
       coverage improves, the core developers will have more standing to
       demand the same of contributed code.

3. Commit sensibly.

   * Each commit should be succinct and singular in focus.
     Refer to `rebasing and squashing`__, above.

     __ rebase_and_squash_

   * Rebase your work atop develop (as `mentioned above`__)
     before creating the PR, or after making any requested
     changes.

     __ rebase_atop_develop_

4. Run ``tox``.

   * 'nough said.

Debugging Tips
--------------

To run one test or a subset of tests, you can specify a substring
expression using the ``-k`` option with ``make test``::

    $ make test TEST_ARGS="-k NAME_OF_TEST_OR_SUB_MODULE"

The substring will be Python-evaluated. As such, you can test multiple
tests using ``or``, e.g., ``-k 'test_method or test_other'``.
Or you can exclude tests using ``not``, e.g., ``-k 'not test_method'``.

Note that ``readline`` functionality will not work from any breakpoint
you encounter under ``make test``. (For example, pressing the Up arrow
will print a control character sequence to the terminal, rather than
showing the last command you ran.)

* If you want to interact with the code at runtime,
  run ``py.test`` directly (see next).

If you'd like to break into a debugger when a test fails, run ``pytest``
directly and have it start the interactive Python debugger on errors::

    $ py.test --pdb tests/

If you'd like a more complete stack trace when a test fails, add verbosity::

    $ py.test -v tests/

    # Or, better yet, two vees!
    $ py.test -vv tests/

If you'd like to run a specific test, use ``-k``, as mentioned above. E.g.,::

    $ py.test -k test__repr__no_start_no_end tests/

Put it all together to quickly debug a broken test. ::

    $ py.test --pdb -vv -k <test_name> tests/

You can also set breakpoints in the code with |pdb|_.
Simply add a line like this:

.. code-block:: python

    import pdb; pdb.set_trace()

For advanced usage, if the code has given up terminal control, e.g.,
if you set a breakpoint in a `Python Prompt Toolkit
<https://github.com/prompt-toolkit/python-prompt-toolkit>`__
handler, you can wrest terminal interactivity back with ``stty``:

.. code-block:: python

    import os, pdb; os.system("stty sane"); pdb.set_trace()

- However, if you want to ``continue`` after fiddling with ``stty sane``,
  you need to restore the settings (by calling ``stty --save`` first,
  debugging, and then calling ``stty`` again with the saved settings),
  which is easiest done from within |dob|_ using helper methods.

  - From within the Carousel, type the ``Alt-=`` key combination to
    break into the debugger.

  - You can also use the 2 helper methods from within the codebase::

      Controller.pdb_break_enter()
      # Poke around, then `c`ontinue!
      Controller.pdb_break_leave()

To test against other Python versions than what is setup in your |virtualenv|_,
you can use |tox|_ and name an environment with the |envlist|_ option::

    $ tox -e <ENVIRONMENT>

For instance::

    $ tox -e py38

The available environments are declared in ``tox.ini``.

Style Guide
-----------

Code style should be readily apparent by reading existing code.

Style Enforcement
^^^^^^^^^^^^^^^^^

The style of new code can be easily and incontrovertibly verified
by running various developer tasks.

1. You can lint the code easily with one command.

   But you have your choice of which one command to run.

   The following three commands are essentially equivalent, and run the code linter:

   .. code-block:: Bash

      # The Makefile lint task:
      $ make lint

      # is similar to the tox task:
      $ tox -e flake8

      # is just like running flake8:
      $ flake8 setup.py dob/ tests/

2. You can lint the docs easily with one or two commands.

   The inline docstrings used to create the documentation can be verified with
   the docstrings linter, which returns nonzero on error. (You can also build
   the docs, but the builder is a little more forgiving and doesn't complain
   as much as the linter.)

   .. code-block:: Bash

      # Run the docstrings linter:
      $ tox -e pydocstyle

      # Generate the reST docs (peruse the output for errors and warnings):
      $ make docs

.. note:: Not all of this author's projects adhere that well to docstrings
          convention, so pep257-compliance is not mandatory. Generally, the
          module docs still build! Also, this author values tests, coverage,
          and readable code over spending time fleshing out docstrings (which
          could be a waste of time during development, as code changes quickly!
          but then there's usually "no time" after development, so we often find
          ourselves with imperfect docstrings littered throughout the code).

          As such, feel free to run the pep257 linter,
          but also feel free not to. It's noisy.

.. _verify-import-statement-order:

3. You can verify import statement order manually.

   Imports are grouped by classification, and then ordered alphabetically
   within each group.

   The |isort|_ tool will automatically fix import statements to conform.

   But |isort|_ also commits certain atrocities such as removing comments
   from ``setup.cfg`` and removing trailing file blank lines, the former
   of which is not easy to work-around, so |isort|_ is not a part of the
   default |tox|_ tasks. You must be run |isort|_ manually.

   .. code-block:: Bash

      $ tox -e isort

   You will likely find that |isort|_ makes unintended changes, and you will
   have to do a selective commit, e.g., ``git add -p <file>``, while reverting
   other changes, e.g., ``git checkout -- setup.cfg``.

Style Reference
^^^^^^^^^^^^^^^

The project style tracks as closely as possible to community conventions,
mostly established in 2001 by Python's creator, Guido van Rossum, and others:

* `PEP 8 -- Style Guide for Python Code <https://www.python.org/dev/peps/pep-0008/>`_

* `PEP 257 -- Docstring Conventions <https://www.python.org/dev/peps/pep-0257/>`_

In lieu of
`PEP 287 -- reStructuredText Docstring Format
<https://www.python.org/dev/peps/pep-0287/>`__,
the project prefers Google-style docstrings, as defined in the
`Google Python Style Guide
<https://google.github.io/styleguide/pyguide.html>`__:

* `Google-style docstrings convention
  <https://google.github.io/styleguide/pyguide.html#381-docstrings>`__

When building the HTML documentation from the sources,
Google-style docstrings are recognized by a
`Sphinx <http://www.sphinx-doc.org/en/master/>`__
extension:

* `napoleon
  <http://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__:
  Support for NumPy and Google style docstrings.

Conventional Deviations
^^^^^^^^^^^^^^^^^^^^^^^

The conventions outlined in `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_
are enforced by the `Flake8 <http://flake8.pycqa.org/en/latest/>`__ linter, with
the following custom rules:

* Use a maximum line length of 89 characters.

  This accommodates two files side-by-side in an editor on a small laptop screen.

  It also makes code more quickly readable, e.g., think of the width of columns
  in a newspaper or magazine.

* *Disabled:* "**W391**: blank line at end of file".

  Ending every file with a blank line accommodates the developer jumping
  their cursor to the bottom of a file in a text editor (say, by pressing
  ``<Ctrl-End>``) and knowing the cursor will always land in the same
  column (rather than landing at the end of some arbitrary-length line).

* *Disabled:* "**W503**: line break before binary operator".

  This produces, IMO, more readable code.

  For instance, write this:

  .. code-block:: Python

      if (some_thing
          and another
          and another_thing):

  or write this:

  .. code-block:: Python

      if (
        some_thing
        and another
        and another_thing
      ):

  but do not write this:

  .. code-block:: Python

      if (some_thing and
          another and
          another_thing):

* *Disabled:* "**W605**: invalid escape sequence".

  This rules incorrectly fires on some regex expression,
  such as ``\d{2}``, thus, shunned.

There are some unwritten rules (because there are unenforceable by
the existing linters, by way of not being features), including:

* Keep methods *small and focused*.

  Use function-level scoping to break up a long method into many
  smaller pieces.

  When you use lots of smaller methods rather than one larger method,
  it has the side effect of forcing you to better document the code,
  by forcing you to consider and assign method names to each function.

  While this project does not need to be strict about method length --
  in Ruby, for instance, the `RuboCop <https://docs.rubocop.org/en/latest/>`__
  linter enforces a `maximum method length
  <https://docs.rubocop.org/en/latest/cops_metrics/#metricsmethodlength>`__
  of 10 lines, by default --
  it's a good idea to strive for shorter methods, and it's not all that
  difficult to do, once you develop your own tricks.

  (For instance, one could write a long function at first, and then break
  it up into smaller, more coherent pieces, selecting multiple lines of code
  at once, hitting ``<Tab>`` to indent the code one stop, then adding ``def``
  lines to each grouping of code and assigning descriptive method names.)

* *Prefer* single quotes over double quotes. (This is a loose rule).

  In other programming languages, like Bash and Ruby, double-quoted strings
  are interpolated, but single-quoted strings are not. This affects whether
  or not certain characters need to be escaped with a delimiter. And it
  can cause unintended consequences, e.g., a developer uses double quotation
  marks but forgets to escape characters within the string.

  One rule we could enforce is to use double quotes for human-readable
  strings, and to use single quotes for all other strings. But human-
  readable strings should already be encased in the localization method,
  e.g., ``_("I'm human-readable!")``, so this demarcation has little
  additional utility.

  So do what feels right in the moment. Oftentimes, using single quotes
  is easiest, because the developer can avoid the Shift key and type the
  quotation mark with one finger.

* Use a single underscore prefix to indicate *private* functions and methods.

  E.g.,: ``def _my_private_method(): ...``.

* Python 2 compatibility has been retired.

  These conventions are no longer necessary (and were removed from the code):

  * Declare the encoding at the top of every file: ``-*- coding: utf-8 -*-``

  * Use *absolute_import* and *unicode_literals* from the ``__future__`` package.

  * Use *six.text_type* to cast a string (to Unicode).

Of Readability
^^^^^^^^^^^^^^

Concerning Writing *Tests, Docstrings, Comments, and Documentation*:

* Strive to write code that is *self-documenting*.

  Use *expressive* variable and methods names (and use long names, if they need to be).

  Break long functions into a collection of shorter methods. This will inherently
  document how the long function works if you give each smaller unit of work a
  descriptive method name.

  Use well-named, intermediate variables to make code more readable, rather than
  writing a long one-liner. By naming intermediate values, you will provide
  inherent documentation to the code.

* Prefer *tests and coverage* over docstrings and documentation.

  You are encouraged to spend your time writing self-documenting code, and to
  develop tests that are illustrative of the usage of the new code, rather than
  worrying about writing docstrings and documentation, which can be tedious and
  time consuming to write (and to read! if you made it this far, dear
  reader!). Written documentation is also likely to become outdated quickly,
  as new code is added and old code is changed, and documents lie in the dust.
  (Which is not to say that docstrings have no utility! Just that docstrings
  are essentially worthless if what you documented has no test coverage, say.)

Just run ``tox``
^^^^^^^^^^^^^^^^

Save for running |isort|_ (`see above`__),
you can run all linter and test tasks with one 3-letter command:

__ verify-import-statement-order_

.. code-block:: Bash

   $ tox

Once this command is passing, you should be good to commit (or rebase) your
work and to submit a `Pull Request`__.

__ `Pull Request Guidelines`_

