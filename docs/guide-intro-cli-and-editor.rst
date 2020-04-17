##########################
Run the Interactive Editor
##########################

============
CLI Commands
============

There are lots of CLI commands, but the most interesting one might be
running the interactive editor, ``dob edit``, which we'll document in
the following sections.

But first, if you'd like to see a list of all dob commands and global
options, use the CLI. Run the command::

  $ dob --help

All of the individual CLI commands are well documented in the CLI itself.

For instance, to get help on the ``export`` command, run::

  $ dob export --help

You'll find other commands for managing the configuration, printing
reports, exporting Facts, adding new Facts from the CLI, and more.

Because all the CLI commands except for the interactive editor are
documented in the CLI, we'll focus here on describing how to use the
interactive editor. We'll leave it as an exercise for the user to
read the CLI help.

==================
Interactive Editor
==================

Run ``dob edit`` to fire up the editor.
::

  $ dob edit

The editor will take over your terminal and look something like this (but nicer)::

  ╭────────────────────────────────────────────────────────────────────────────────╮
  │             Thu 16 Apr 2020 ◐ 02:13 PM — 03:52 PM                              │
  ╰────────────────────────────────────────────────────────────────────────────────╯

    duration........... :  1 hour  39 minutes
    start.............. : 2020-04-16 14:13:49
    end................ : 2020-04-16 15:52:50 <now>
    activity........... : Documentation
    category........... : dob Development
    tags............... : #readme

  ┌────────────────────────────────────────────────────────────────────────────────┐
  │Working on the "Interactive Editor" help.                                       │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  │                                                                                │
  └────────────────────────────────────────────────────────────────────────────────┘
  Fact ID #22619                              [?]: Help / [C-S]: Save / [C-Q]: Quit

You can press ``?`` in the app to see a short list of commands and keys.

But a more complete list of editor commands is actually in the config —
because all of the key bindings in the editor are configurable!

========================
Set your own keybindings
========================

To see the list of editor commands and their keybindings,
look under the ``editor-keys`` section, e.g.,::

  $ dob config dump editor-keys
  +-------------+-----------------------+----------------------+----------------------+
  |   Section   |         Name          |   Value <Default>    |         Help         |
  +=============+=======================+======================+======================+
  | editor-keys | focus_next            | tab                  | Switch to Next       |
  |             |                       |                      | Widget (description  |
  |             |                       |                      | → start time → end   |
  |             |                       |                      | time → [repeats])    |
  +-------------+-----------------------+----------------------+----------------------+
  | editor-keys | focus_previous        | s-tab                | Switch to Previous   |
  |             |                       |                      | Widget (description  |
  |             |                       |                      | → end time → start   |
  |             |                       |                      | time → [repeats])    |

In this snippet, you'll see that ``Tab`` is mapped to the ``focus_next``
command, and that ``Shift-Tab`` is mapped to ``focus_previous``.

Note, too, that dob supports *multiple* mappings to the same command.

- For example, in Vim, there are multiple undo command mappings,
  which dob emulates::

    $ dob config get editor-keys undo_command
    [["c-z"], ["u"]]

  By default, both ``Ctrl-z`` and ``u`` are mapped to undo, just like in Vim.

- If you want to use multiple mappings, express the value as a JSON-encoded
  array of arrays.

  Why an array of arrays? Because dob supports *multiple keypress* bindings.

  For instance, the command to copy the Activity from the current Fact is
  ``A`` followed by ``Ctrl-c``, which is expressed as an array within an array::

    $ dob config get editor-keys fact_copy_activity
    [["A", "c-c"]]

  Note that the single outer array contains *one* inner array with *two* elements,
  which represent the two-key mapping.

- Finally, be aware that Alt-key (or Option-key) mappings are indicated
  using a two-key mapping sequence with 'escape' as the first element,
  e.g., pressing ``Alt-left`` (the Alt key and the left arrow key
  simultaneously) looks like this::

    [["escape", "left"]]

  In dob, by default, the ``J`` key is also mapped to the same command,
  so the actual config entry looks like this::

    $ dob config get editor-keys jump_day_dec
    [["J"], ["escape", "left"]]

========================================
Show all editor commands and keybindings
========================================

If you'd like to page the (long) config-dump output, you could, say,
pipe it to ``less``, or you could specify a global CLI option, ``--pager``.

For example, these two commands are essentially equivalent::

  $ dob config dump editor-keys | less

  $ dob --pager config dump editor-keys

