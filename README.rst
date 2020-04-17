@@@
dob
@@@

.. image:: https://api.travis-ci.com/hotoffthehamster/dob.svg?branch=develop
  :target: https://travis-ci.com/hotoffthehamster/dob
  :alt: Build Status

.. image:: https://codecov.io/gh/hotoffthehamster/dob/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/hotoffthehamster/dob
  :alt: Coverage Status

.. image:: https://readthedocs.org/projects/dob/badge/?version=latest
  :target: https://dob.readthedocs.io/en/latest/
  :alt: Documentation Status

.. image:: https://img.shields.io/github/v/release/hotoffthehamster/dob.svg?style=flat
  :target: https://github.com/hotoffthehamster/dob/releases
  :alt: GitHub Release Status

.. image:: https://img.shields.io/pypi/v/dob.svg
  :target: https://pypi.org/project/dob/
  :alt: PyPI Release Status

.. image:: https://img.shields.io/github/license/hotoffthehamster/dob.svg?style=flat
  :target: https://github.com/hotoffthehamster/dob/blob/master/LICENSE
  :alt: License Status

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |pip| replace:: ``pip``
.. _pip: https://pip.pypa.io/en/stable/

.. |demo-dob| replace:: *demo dob*
.. _demo-dob: `demo dob`_

|dob|_ is an interactive, terminal-based time tracking application.

You'll find Vim-like navigation,
robust functionality,
a customizable user experience,
lots of great plugins, and
an elegant, minimalistic interface.

``dob`` is written in `Python <https://www.python.org/>`__
and installs easily with |pip|_:

.. code-block:: sh

    $ pip3 install dob

The best way to learn ``dob`` is to run the demo:

.. code-block:: sh

    $ dob demo

For other setup options, read the
`installation guide
<https://dob.readthedocs.io/en/latest/installation.html>`__.

##########
Quick Peak
##########

dob has lots of CLI commands, and it also includes an interactive terminal application.

Here's a little taste of what the terminal application looks like.::

  ╭────────────────────────────────────────────────────────────────────────────────╮
  │             Thu 16 Apr 2020 ◐ 02:13 PM — 03:52 PM                              │
  ╰────────────────────────────────────────────────────────────────────────────────╯

    duration........... :  1 hour  39 minutes
    start.............. : 2020-04-16 13:13:49
    end................ : 2020-04-16 14:52:50
    activity........... : dobumentation
    category........... : dob Development
    tags............... : #readme

  ┌────────────────────────────────────────────────────────────────────────────────┐
  │I'm adding this Fact to the README. So meta.                                    │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  └────────────────────────────────────────────────────────────────────────────────┘
  Fact ID #22618                              [?]: Help / [C-S]: Save / [C-Q]: Quit

Though in your terminal, you'll see colors and font ornamentation
(bold, italic, and underline).

######
Status
######

.. |beta| replace:: *beta*
.. _beta: https://en.wikipedia.org/wiki/Software_release_life_cycle#Beta

``dob`` is released to |beta|_!

* You can |demo-dob|_ to see how awesome it is!

* You could also start using ``dob``, but just be aware it
  has not been vetted yet for a larger audience — we've only
  tested on one OS so far!

  We just don't want you to have a bad first experience.

  Aka, *you've been warned!*

We'll stop calling dob a beta once it's been tested on more OSes.

But dob is already feature-rich, and it's used daily (hourly!) by
the authors.

To see what all the fuss is about, you can ``pip3 install dob``
and run ``dob demo`` right now to try it out.

Or, keep reading for an overview of dob, a list of its features,
and then detailed documentation of the interactive editor commands.

#####
Ethos
#####

``dob`` is a designed for developers, but suitable
for any individual whose comfortable in the terminal.

``dob`` is perfect for the person who asks,
*Why must I use my mouse to manage time tracking?*

``dob`` is even more suited for the person who asks,
*How can I manage time tracking with the fewest possible keystrokes?*

``dob`` is inspired by
`Hamster <https://github.com/projecthamster/>`__,
a beloved but aged time tracking application for
`GNOME <https://en.wikipedia.org/wiki/GNOME>`__.

``dob`` is emulative of `Vim <https://www.vim.org/>`__,
an editor that enables users to concentrate on their
work while the tool itself slips into the background.

Try ``dob`` today -- you might like it!

- `Demo dob`_ to learn it.

- | Then, `start from scratch`__,
  | or `load a legacy database`__.

__ https://dob.readthedocs.io/en/latest/usage.html#start-fresh

__ https://dob.readthedocs.io/en/latest/usage.html#upgrade-hamster

If you like |dob|_, hopefully you'll
`help us make it better
<https://dob.readthedocs.io/en/latest/contributing.html>`_!

########
Features
########

- Minimalist interactive console app fits elegantly into your terminal-based workflow.

- Robust configuration -- and manageable via CLI if you want to avoid the config file.

- Fully customizable -- change which keys map to which commands.

- Define your own user-specific paste commands -- assign your own activities and tags.

- Undo and redo edits as you work -- don't worry if you make a mistake.

- Auto-complete makes it easy to set activities and tags -- and shows useful stats, too.

- Edit text in your favorite ``$EDITOR`` -- and set a file extension for highlighting.

- Use all the Unicode you want -- spice up your notes!

- Personalize the interface colors -- you can even style your own activity and tag names!

- Natural syntax lets you go "offline" and dob to a text file, that you can import later.

- Migrates legacy Hamster databases -- and repairs integrity issues, too.

- Supports unrestricted plugin access -- anyone can add their own commands and config.

- Includes command shortcuts -- common command sequences mapped to a single keypress.

- Runs on the latest Python (3.6, 3.7, and 3.8).

- Suitably tested (though coverage could be better).

- Well documented -- get help at runtime, on the command line, or online.

- Simple, smooth code base -- follows best practices, and uses top libraries.

- Low bar of entry to get raw access to data --
  defaults to `Sqlite3 <https://www.sqlite.org/index.html>`_ file.

- Constant dogfooding *(-- I dob daily!)*

- Free and open source -- hack away!

####
Demo
####

Demo ``dob``
============

Run the ``demo`` command to load an interactive tutorial:

.. code-block:: sh

    $ dob demo

And then follow the walk-through.

###############
Getting started
###############

Read `basic usage`__ to learn how to create an empty data store,
or how to import an existing database.

__ https://dob.readthedocs.io/en/latest/usage.html

############
Learning dob
############

You'll find lots of documentation online, including:

- `Configure dob`__

- `Choose your $EDITOR`__

- `Run the Interactive Editor`__

- `Exit, Save, and Undo/Redo`__

- `Navigate Facts Quickly`__

- `Edit Facts and Metadata`__

- `Copy and Paste Metadata`__

- `Useful Command Combinations`__

- `Nudge Start and End Time`__

__ https://dob.readthedocs.io/en/latest/guide-config.html
__ https://dob.readthedocs.io/en/latest/guide-editor-env.html
__ https://dob.readthedocs.io/en/latest/guide-intro-cli-and-editor.html
__ https://dob.readthedocs.io/en/latest/guide-exit-save-undoredo.html
__ https://dob.readthedocs.io/en/latest/guide-jumping-around.html
__ https://dob.readthedocs.io/en/latest/guide-editing-facts.html
__ https://dob.readthedocs.io/en/latest/guide-copy-paste.html
__ https://dob.readthedocs.io/en/latest/guide-combinations.html
__ https://dob.readthedocs.io/en/latest/guide-nudging-time.html

#######
Plugins
#######

Plugins make it easy for everyday dobbers to write their own
features and to share them with the broader community.

The core development team has created the following plugins
for non-essential and distribution-specific features.

*Please note: these plugins are not yet published!*
(We just want to get you excited in the meantime.)

- The ``dob-plugin-export-commit``
  plugin exports and commits changes to your dob database on every save.

- The ``dob-plugin-stale-fact-goader``
  plugin displays a GNOME-style popup notification after some amount of
  inactivity to badger you to start a new Fact.

- The ``dob-plugin-git-hip``
  plugin tags the active Fact based on the Git branch name
  pulled from the current directory.

Have a great idea for ``dob``? Implement it as a plugin!

- Plugins have complete access to dob.

  Plugins can add their own commands.

  Plugins can add their own configuration.

  Plugins can run on startup, on exit, or whenever the user saves.

Plugins help keep ``dob`` lean, and they let you turn
an idea into a feature quickly and easily!

#######
Thanks!
#######

We hope you enjoy using dob as much as we have had making it!

And if you like it, please tell your friends and colleagues about it.
Tell the whole world!!

Keep on dobbin'!

