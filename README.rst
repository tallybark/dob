@@@
dob
@@@

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

.. |demo| replace:: *demo dob*
.. _demo: `demo dob`_

|dob|_ is an interactive, terminal-based time tracking application.

You'll find Vim-like navigation,
robust filtering and searching capabilities,
and a colorful, customizable interface.

``dob`` is written in `Python <https://www.python.org/>`__
and installs easily with |pip|_:

.. code-block:: sh

    $ pip install dob

The best way to learn ``dob`` is to run the demo:

.. code-block:: sh

    $ dob demo

For other setup options, read the
`installation guide
<https://dob.readthedocs.io/en/latest/installation.html>`__.

.. |alpha-software| replace:: *alpha* software
.. _alpha-software: https://en.wikipedia.org/wiki/Software_release_life_cycle#Alpha

**ALPHA ALERT!** ``dob`` is |alpha-software|_.
A proper, stable release is forthcoming
`this year
<https://www.timeanddate.com/countdown/to?iso=20191231T235959&p0=%3A&msg=dob+alpha+egress&font=cursive>`_!

* You can currently |demo|_.

* You can even start using ``dob`` today, but the developers are
  finishing a few features, and shoring up test coverage.

  And we would not want you to get frustrated, or to file bugs for issues
  we already plan to fix. So please be patient!

  (You may see progress by fits and starts, but *it'll happen.*)

* Please be aware that real humans have only tested the alpha code
  on *Debian Linux* (technically, `Linux Mint <https://linuxmint.com/>`_).

  *We'll verify macOS and Windows support as part of the alpha cycle.*

#####
Ethos
#####

``dob`` is a developer's tool, or at least targeted to someone who’s
comfortable in the terminal.

``dob`` is perfect for the person who asks,
*Why must I use my mouse to manage time tracking?*

``dob`` is inspired by
`Hamster <https://projecthamster.wordpress.com/>`__,
a beloved but aged time tracking application for
`GNOME <https://en.wikipedia.org/wiki/GNOME>`__.

.. Give |dob|_ a try, and you might like it.

.. - You can `Demo dob`_, `Import a legacy database`__, or `Start from scratch`__.
.. - You can `demo dob`_, `import a legacy database`__, or `start from scratch`__.

.. Give |dob|_ a try, and you might like it!

Try ``dob`` today -- you might like it!

- `Demo dob`_ to learn it.

- Then, `start from scratch`__,

  or `load a legacy database`__.

__ https://dob.readthedocs.io/en/latest/usage.html#start-fresh

__ https://dob.readthedocs.io/en/latest/usage.html#upgrade-hamster

If you like |dob|_, hopefully you'll
`help us make it better
<https://dob.readthedocs.io/en/latest/contributing.html>`_!

########
Features
########

* Compatible with all modern Python releases (3.5, 3.6, and 3.7).
* Seamlessly integrates into your terminal-based workflow.
* Naturally Unicode compatible -- spice up your notes!
* Can migrate legacy Hamster databases (and fix integrity issues, too).
* Excellent coverage (to give you comfort knowing your Facts are safe).
* Well documented features -- get help at runtime, or on the command line.
* Simple, elegant code base -- follows best practices, uses top libraries.
* Low bar of entry to get raw access to data --
  defaults to `Sqlite3 <https://www.sqlite.org/index.html>`_ file.
* Constant dogfooding *(-- I dob daily!)*
* Free and open source -- hack away!

#######
Example
#######

Demo ``dob``
============

You can easily demo ``dob`` after installing it.

Run the ``demo`` command to load an interactive tutorial:

.. code-block:: sh

    $ dob demo

`Keep reading`__ to learn how to create an empty data store,
or how to import an existing database.

__ https://dob.readthedocs.io/en/latest/usage.html

