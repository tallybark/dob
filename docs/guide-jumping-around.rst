#####################
Navigate (Jump) Facts
#####################

Continuing along the Vim theme, use ``j`` and ``k`` to navigate Facts.

=================================
Jump to the next or previous Fact
=================================

- ``j`` will change to the previous Fact, and ``k`` will navigate to
  the next Fact.

- Or use the ``left`` and ``right`` arrow keys.

================================
Jump forward or backward one day
================================

You can jump greater distances, too.

- Use ``J`` (capital 'J') to go back one day.

  Or use ``K`` (capital 'K') to jump forward a day.

  You can also use ``Alt-left`` and ``Alt-right``, respectively.

===========================================
Jump all the way to the first or final Fact
===========================================

You can jump all the way backward or all the way forward in time
(to the first or final Fact) using a few different commands:

- Use ``f`` to go to the *final* saved Fact, and use ``F`` (capitalized)
  to go to the *first* saved Fact.

- The Vim-like commands, ``gg`` and ``G``, will also jump all the way
  backwards and forwards, respectively.

  But the ``gg`` and ``G`` commands will land on a *gap* Fact, if one exists.

  - There will always be a *gap* Fact before your first Fact. (This
    allows you to add a new Fact before the first Fact, if you wish.)

    And there will sometimes be a *gap* Fact after your final Fact,
    unless your final Fact is active (has no end time) and has been
    edited with an Activity, Tag, or Description.

  The ``G`` command is mostly useful for ensuring you always jump to
  the fact at time "now", whereas the ``f`` command ensures you always
  jump to a real Fact, be it the active Fact, or the last ended Fact.

==================================
Modify Jump commands with a prefix
==================================

You can type a *count* prefix or a *date* prefix before the jump commands
to change their behavior. *(Vim users should recognize this feature!)*

==============
Jump *n* Facts
==============

To jump more than one Fact at a time, add a count modifier to either the
``j`` or the ``k`` command.

- For instance, to jump back five Facts, type ``5j``.

=============
Jump *n* days
=============

To jump more than one day at a time, add a count modifier to either
of the ``J`` or ``K`` commands.

- For instance, to jump forward six and a half days, type ``6.5K``.

===============================
Jump to a specific date or time
===============================

Finally, you can jump to a specific data (and time) using a date
prefix before any of the ``f``, ``F``, ``G``, or ``gg`` commands
(they'll each behave the same way).

- For example, ``20200410G`` will jump to the first Fact on 2020-04-10.

- If you want to use punctuation, that works, too.

  - For instance, in addition to ``20200101G`` to jump to New Year's day,
    you can instead type ``2020-01-01G``, or even ``2020/01/01G``.

    See the ``date_separators`` config value for the list of acceptable
    characters besides numbers that you can use — it defaults to the following:
    ``-`` ``/`` ``t`` ``T`` ``:`` and the ``Space`` character.

- If you want to jump to a specific time on a specific date, use clock time.

  - For example, typing ``100G`` will jump to the Fact at 1:00 AM today.

    Or type ``2020/01/01 1400G`` or more simply ``2020010114G``
    to jump to 2p on New Year's day, 2020.

    Or use `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`__ syntax
    and type ``2020-01-01T14:00G``

