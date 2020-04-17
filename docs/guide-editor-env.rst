############################
Choose your Text ``$EDITOR``
############################

dob runs your preferred text editor when you edit the Fact description.

Make sure that the ``$EDITOR`` environment variable is set to something
reasonable before running dob.

The author (obviously a big Bramboy, er, fanboy, from comments elsewhere)
loves Vim — and sets the ``EDITOR`` variable from their user's Bash startup
scripts.

You can also set or change the variable whenever you want from the terminal,
e.g.,::

  $ EDITOR=/usr/bin/vim
  $ dob edit

Then when you edit a Fact description, dob runs Vim
(or whatever editor you've got configured).

In your text editor, write the Face description, then save and quit.
You'll be returned to dob, where you'll see the updated description text.

And if you make some edits you don't care for, you can either
quit the text editor without saving, or you can save and quit the
text editor, and then use the undo feature in dob (e.g., press ``Ctrl-z``).

===============================
Text Editor Syntax Highlighting
===============================

If your text editor enables syntax highlighting based on the
file extension, you can tell dob to set one.

For instance, the author likes to write notes in
`reStructuredText <https://docutils.sourceforge.io/rst.html>`__
format, so they've assigned the ``.rst`` file extension.

Their config file includes this entry::

  [term]
  editor_suffix = .rst

which you could set easily from the CLI, e.g.,::

  $ dob config set term editor_suffix .rst

Obviously, Markdown can be configured just as easily::

  $ dob config set term editor_suffix .md

