#######################
Copy and Paste Metadata
#######################

===================
Copy/Paste Metadata
===================

If you'd like to copy the Activity, Category, and Tags
(collectively called the *metadata*) from one Fact to
another, use ``Ctrl-c`` and ``Ctrl-v``.

- Find the Fact whose metadata you'd like to copy, and press ``Ctrl-c``.

- Then jump to the Fact you want to apply it to, and press ``Ctrl-v``.

You can also choose just a single metadata value to copy, by
adding a prefix key before ``Ctrl-c``:

- To copy only the Activity\@Category, type ``A``, then ``Ctrl-c``.

- Likewise, to copy only the Tags, press ``T`` and then ``Ctrl-c``.

- You can also copy the description with ``D`` and then ``Ctrl-c``.

Then just ``Ctrl-v`` paste like you normally would.

======================
Ornate Paste Shortcuts
======================

dob offers a few commonly executed command sequences as one command,
such as pasting any Fact's metadata to the final, active Fact.

- Press ``Ctrl-e`` to copy the current Fact's metadata and apply
  it to the final Fact.

You can also paste-forward the current Fact's metadata to a *new* Fact.

- Press ``V`` if you'd like to copy the metadata to a new Fact,
  starting "now".

  dob will copy the current Fact's metadata, jump to the final fact,
  stop it, go "right" to the new active Fact, and then paste the metadata.

=====================
Custom Paste Commands
=====================

You can define your own custom key bindings for pasting arbitrary Fact metadata.

You can apply any combination of Activity\@Category, Tags, and description.

Just add two settings to your user config for each custom mapping.

- One setting specifies the Factoid to parse,
  and the other is the key binding to use.

  - Nest them under the ``[custom-paste]`` config section.

  - Name one using the prefix, ``factoid_``, followed by a
    number from ``1`` to ``28``.

    Name the other using the prefix, ``mapping_``, followed
    by the same number.

- For instance, within ``~/.cache/dob/dob.conf``, here are
  some custom mappings::

      [custom-paste]

      # Paste act@gory and 2 Tags:
      factoid_1 = "Tea@Personal: #biscuit #zinger"
      mapping_1 = f4

      # Paste act@gory, 1 tag, and a description (if not already set):
      factoid_2 = "Tickets@Project: #num-1234: Working on baloney."
      mapping_2 = f5

      # Paste a few Tags (the @: is required):
      factoid_3 = "@: #tag-1 #tag-2"
      mapping_3 = f6

      # Paste a mere description:
      factoid_4 = "#this is not a tag"
      mapping_4 = f7

  In this example, press ``F4``, or ``F5``, etc., to apply that
  command's metadata to the current Fact.

  Note that there's an arbitrary limit of 28 such custom paste commands.
  I.e., the last pair dob looks for is ``factoid_28`` and ``mapping_28``.

- See ``dob add --help`` for more help on the so-called *Factoid* format.

  Or just follow the formats in the example above.

