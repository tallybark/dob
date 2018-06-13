============
Contributing
============

Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given (if so desired).

.. contents::
   :depth: 2

Types of Contributions
----------------------

You can contribute in many ways:

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/hotoffthehamster/dob/issues.

If you are reporting a bug, please include:

* Your operating system name and version; and the Python version you are using.

* Any details about your local setup that might be helpful for troubleshooting.

* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs.
Anything tagged with "bug" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features.
Anything tagged with "feature" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

``dob`` can always use more-better docs, whether as part of the official
user or developer READMEs, in the code as docstrings, or even on the web
as blog posts, articles, etc.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/hotoffthehamster/dob/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome!
* Be nice, please, and don't expect premium service!!

Get Started!
------------

.. |virtualenvwrapper| replace:: ``virtualenvwrapper``
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/

Ready to contribute? Here's how to set up ``dob`` for local development.

1. Fork the ``dob`` and ``nark`` repos on GitHub.

   * Visit `<https://github.com/hotoffthehamster/dob>`_ and click *Fork*.

   * Visit `<https://github.com/hotoffthehamster/nark>`_ and click *Fork*.

2. Clone your fork locally.

   Open a local terminal, change to a directory you'd like to develop from,
   and run the command::

    $ git clone git@github.com:<your_login>/dob.git

    $ git clone git@github.com:<your_login>/nark.git

3. Install both projects into a Python virtual instance, or ``virtualenv``.

   First, ensure that you have |virtualenvwrapper|_ installed.

   Next, set up a virtual environment for local development::

    $ cd dob/
    $ mkvirtualenv -a $(pwd) dob

   *Note:* We use the ``-a`` option so that ``cdproject`` changes directories
   to the ``dob/`` directory when we're in the virtual environment.

   Next, set up your forks for local development::

    (dob) $ cdproject
    (dob) $ make develop
    (dob) $ cd ../nark
    (dob) $ make develop

   *Hint:* As usual, run ``workon`` to activate the virtual environment, and
   ``deactivate`` to leave it. E.g.,::

    # Load the Python virtual instance.
    $ workon dob
    (dob) $

    # Do your work.
    (dob) $ ...

    # Finish up.
    (dob) $ deactivate
    $

4. Before starting work on a new feature or bugfix, make sure your
   ``develop`` branch is up to date with the official branch::

    (dob) $ cdproject
    (dob) $ git remote add upstream git@github.com:hotoffthehamster/dob.git
    (dob) $ git fetch upstream
    (dob) $ git checkout develop
    (dob) $ git rebase upstream/develop
    (dob) $ git push origin HEAD
    # And do the same for ../nark.

5. Create a branch for local development. If you are working on an
   known issue, reference the Issue number in the branch name, e.g.,::

    (dob) $ git checkout -b feature/ISSUE-123-name-of-your-issue

   Now you can add and edit code in your local working directory.

6. Do your work and make one or more sane, concise commits::

    (dob) $ git add -p
    (dob) $ git commit -m "<Category>: <Short description of changes.>

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

     (You'll notice that this strategy is similar to
     `gitmoji <https://gitmoji.carloscuesta.me/>`__,
     but it's more concise, and less obtuse.)

7. Throughout development, run tests and the linter -- and definitely before
   you submit a Pull Request.

   ``dob`` uses |flake8|_ for linting, |pytest|_ for unit testing,
   and |tox|_ for verifying against the many versions of Python.

   You can run all of these tools with one command::

    (dob) $ make test-all

   .. FIXME: Verify that `test-all` runs flake8 and tox.

   .. FIXME: I think this hint is not needed (either flake8 and tox
   ..        are already installed, `make develop` finds them, not sure).

   (*Hint:* To get ``flake8`` and ``tox``, just ``pip install`` them into
   your ``virtualenv``.)

    .. FIXME/2018-05-16: (lb):
    ..    pip install -U -r requirements/test.pip

   .. _rebase_and_squash:

8. Rebase and squash your work, if necessary, before submitting a Pull Request.

   E.g., if the linter caught an error, rather than making a new commit
   with just the linting fix(es), make a temporary commit with the linting
   fixes, and then squash that commit into the previous commit wherein
   you originally added the code that didn't lint.

   (*Note:* Rebasing is an intermediate Git skill, but you needn't be
   afraid. Just bear in mind that you should not rebase any branch that
   other developers are working on (which should not apply to your working
   branch, unless you are collaborating with others, which you're probably
   not). And know that ``git rebase --abort`` is your friend (though you might
   want to make a copy of your local working directory before rebasing, just
   to be safe; or at least make a new branch from the current ``HEAD``).)

   For example, pretend that I have the following git history::

    (dob) $ git log --oneline | head -3

    b1c07a4 Regression: Fix some old bug.
    17d1e38 Feature: Add my new feature.
    2e888c3 Bugfix: Oops! Did I do that?

   and then I commit a linting fix that should have been included with
   the second-to-last commit, ``17d1e38``.

   First, add the linting fix::

    (dob) $ git add -A
    (dob) $ git ci -m "Squash me!"

   Next, start a rebase::

    (dob) $ git rebase -i 2e888c3

   (*Note:* Use the SHA1 hash of the commit *after* the one you want squash into.)

   Git should open your default editor with a file that starts out like this::

    pick 2e888c3 Bugfix: Oops! Did I do that?
    pick 17d1e38 Feature: Add my new feature.
    pick b1c07a4 Regression: Fix some old bug.
    pick f05e080 Squash me!

   Reorder the commit you want to squash so that it's after the commit
   you want to combine it with, and change the command from ``pick`` to
   ``squash`` (or ``s`` for short)::

    pick 2e888c3 Bugfix: Oops! Did I do that?
    pick 17d1e38 Feature: Add my new feature.
    squash f05e080 Squash me!
    pick b1c07a4 Regression: Fix some old bug.

   Save and close the file, and Git will rebase your work.

   When Git rebases the commit being squashed, it will pop up your editor
   again so you can edit the commit message of the new, squashed commit.
   Delete the squash comment (``Squash me!``), and save and close the file.

   Git should hopefully finish up and report, ``Successfully rebased and updated``.

   (If not, you can manually resolve any conflicts. Or, you can run
   ``git rebase --abort`` to rollback to where you were before the rebase,
   and you can look online for more help rebasing.)

9. Push the changes to your GitHub account.

   After testing and linting, and double-checking that your new feature or
   bugfix works, and rebasing, and committing your changes, push them to
   the branch on your GitHub account::

    (dob) $ git push origin feature/ISSUE-123-name-of-your-issue

   *Note:* If you pushed your work and then rebased, you may have to force-push::

    (dob) $ git push origin feature/ISSUE-123-name-of-your-issue --force

   .. _rebase_atop_develop:

10. Finally,
    `submit a pull request <https://github.com/hotoffthehamster/dob/pulls>`_
    through the GitHub website.

    *Important:* Please rebase your code against ``develop`` and resolve
    merge conflicts, so that the main project maintainer does not have
    to do so themselves. E.g.,::

     (dob) $ git checkout feature/ISSUE-123-name-of-your-issue
     (dob) $ git fetch upstream
     (dob) $ git rebase upstream/develop
     # Resolve any conflicts, then force-push.
     (dob) $ git push origin HEAD --force
     # And then open the Pull Request.

.. |virtualenvwrapper| replace:: ``virtualenvwrapper``
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/

.. |flake8| replace:: ``flake8``
.. _flake8: http://flake8.pycqa.org/en/latest/

.. |pytest| replace:: ``pytest``
.. _pytest: https://docs.pytest.org/en/latest/

.. |tox| replace:: ``tox``
.. _tox: https://tox.readthedocs.io/en/latest/

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. Update docs.

   * Use docstrings to document new functions, and use inline comments
     as appropriate (longer comments should go into a reST file in the
     ``docs/`` directory).

   * Update ``README.rst`` if your feature adds to or changes the API.

2. Include tests.

   * If the pull request adds new functions, they should be tested,
     either implicitly, because they're already called by an existing
     test. Or they should be called explicitly, because you added new
     tests for them.

   * We strive for 100% test coverage, but we do not enforce it.
     In the least, your code should not reduce coverage.

3. Commit sensibly.

   * Each commit should be succinct and singular in focus.
     Refer to `rebasing and squashing`__, above.

     __ rebase_and_squash_

   * Rebase your work atop develop (as `mentioned above`__)
     before creating the PR, or after making any requested
     changes.

     __ rebase_atop_develop_

4. Run ``make test-all``.

   * 'nough said.

Debugging Tips
--------------

To run one test or a subset of tests, you can specify a substring
expression using the ``-k`` option with ``make test``::

    $ make test TEST_ARGS="-k NAME_OF_TEST_OR_SUB_MODULE"

The substring will be Python-evaluated. As such, you can test multiple
tests using ``or``, e.g., ``-k 'test_method or test_other'``.
Or you can exclude tests using ``not``, e.g., ``-k 'not test_method'``.

If you want to run a particular ``tox`` environment, you can run
``tox`` with the ``envlist`` option::

    $ tox -e NAME_OR_ENVIRONMENT

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

You can also set breakpoints in the code with ``pdb``.
Simply add a line like this:

.. code-block:: python

    import pdb; pdb.set_trace()

And that's it!

**🐹appy 🐹amster 🐹acking!!1**

