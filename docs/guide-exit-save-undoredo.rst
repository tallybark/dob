#########################
Exit, Save, and Undo/Redo
#########################

========
Exit dob
========

No command tutorial for a keyboard-only interface would be
complete unless you first knew how to exit the app (here's
looking at you, Vim).

- Press ``Ctrl-q`` to exit.

  If you have unsaved changes, you'll be prompted to save. You can press
  ``y`` to really exit or ``n`` to go back to the app, or you can mash
  ``Ctrl-q`` twice more and dob will really let you out.

- Press ``q`` to exit easily if you have no unsaved changes.

- Or type the Vim-esque colon-command ``:q`` followed by ``Enter``.

====
Save
====

If you guessed ``Ctrl-s``, you'd be right.

- You can also type ``:w`` and ``Enter``, in honor of Vim.

- Or you can type ``:wq`` and ``Enter`` to write and quit.

=========
Undo/Redo
=========

You can undo and redo edits just like in any decent editor.

When you undo a change, dob will change to the Fact whose changes are
being undone, and dob will then undo whatever edit you last made (be it
to the start or end time, the activity and category, the tags, and/or
the description).

The undo and redo keys are mapped to the same keys as in Vim.

- To undo, press either ``Ctrl-z`` or ``u``.

- To redo an undo, press either ``Ctrl-y``, ``Ctrl-r``, or ``r``.

If you'd like to remove or change any of these mappings,
look for the two config options under the ``editor-keys`` section:
``undo_command`` and ``redo_command``.

