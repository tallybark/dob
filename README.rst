###
dob
###

.. image:: https://travis-ci.com/hotoffthehamster/dob.svg?branch=develop
  :target: https://travis-ci.com/hotoffthehamster/dob
  :alt: Build Status

.. image:: https://codecov.io/gh/hotoffthehamster/dob/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/hotoffthehamster/dob
  :alt: Coverage Status

.. image:: https://readthedocs.org/projects/dob/badge/?version=latest
  :target: https://dob.readthedocs.io/en/latest/
  :alt: Documentation Status

.. image:: https://img.shields.io/github/release/hotoffthehamster/dob.svg?style=flat
  :target: https://github.com/hotoffthehamster/dob/releases
  :alt: GitHub Release Status

.. image:: https://img.shields.io/pypi/v/dob.svg
  :target: https://pypi.org/project/dob/
  :alt: PyPI Release Status

.. image:: https://img.shields.io/github/license/hotoffthehamster/dob.svg?style=flat
  :target: https://github.com/hotoffthehamster/dob/blob/develop/LICENSE
  :alt: License Status

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |pip| replace:: ``pip``
.. _pip: https://pip.pypa.io/en/stable/

|dob|_ is an interactive, terminal-based time tracking application.
It's got Vim-like navigation, robust filtering and searching
capabilities, and a colorful, customizable interface.

Install with |pip|_::

    pip3 install dob

For more options, read the
`installation guide <https://dob.readthedocs.io/en/latest/installation.html>`__.

.. NOTE:: Please be aware that |dob|_ is currently *alpha* software.

          The application works well, but it has a few minor issues
          that must be fixed before it can be truly released. And it
          wouldn't hurt to write a few more tests and expand coverage.

          In lieu of committing to a date that this software will be
          out of alpha, let's just say, hopefully this year!

=====
Ethos
=====

|dob|_ is a developer's tool, or at least targeted to someone whose
comfortable in the terminal.

|dob|_ is perfect for the person who asks,
*Why must I use my mouse to manage time tracking?*

|dob|_ is inspired by
`Hamster <https://projecthamster.wordpress.com/>`__,
a beloved but aged time tracking application for
`GNOME <https://en.wikipedia.org/wiki/GNOME>`__.

Give |dob|_ a try, and you might like it.

- You can `Demo dob`_, `Import a legacy database`__, or `Start from scratch`__.

__ https://dob.readthedocs.io/en/latest/installation.html#upgrade-legacy-database
__ https://dob.readthedocs.io/en/latest/installation.html#start-fresh

If you like |dob|_, hopefully you'll help us make it better!

========
Features
========

* Compatible with all current Python releases (3.5, 3.6, and 3.7).
* Seamlessly integrates into your terminal-based workflow.
* Naturally Unicode compatible -- spice up your notes!
* Fully Timezone-aware -- don't lose time traveling!
* Can migrate legacy Hamster databases (and fix integrity issues, too).
* Excellent coverage (to give you comfort knowing your Facts are safe).
* Well documented features -- at runtime, or on the command line.
* Simple, elegant code base -- follows best practices, uses top libraries.
* Low bar of entry to get raw access to data -- defaults to Sqlite3 store.
* Constant Dogfooding -- I ``dob`` *daily!*
* Free and open source -- hack away!

See how you can
`contribute
<https://dob.readthedocs.io/en/latest/contributing.html>`__
to the project.

=======
Example
=======

Demo |dob|_
-----------

You can easily demo |dob|_ without configuring the database.

Run the ``demo`` command to load an interactive tutorial:

.. code-block:: Bash

   $ dob demo

`Keep reading`__ to learn how to create an empty data store,
or to import an existing database.

__ https://dob.readthedocs.io/en/latest/usage.html

