########################
Nudge Start and End Time
########################

In addition to editing the time directly as described earlier,
you can use a number of special commands to nudge time.

=============================
Setting the end time to "now"
=============================

One of the most common operations you'll perform is stopping a Fact
and starting a new one.

There can be only one active Fact in dob, and it'll be the final, latest
Fact in your data set.

- Two of the Combination Commands described earlier, ``V`` and ``Ctrl-e``,
  will stop a Fact and set its end time to "now".

- You can also press ``e`` to edit the end time directly (or use ``Tab``
  to change the focus to the end time widget).

  - If the cursor is on the end time, you can press ``Enter`` to set it.

    For example, assume the active Fact end time shows this::

      end................ : 2020-04-16 20:31:49 <now>

    If you press ``Enter`` on the end time, and then press ``e``
    again or ``Tab`` to change focus, dob will set the end time
    to the current time ("now"), and then show you a diff of the
    changes, e.g.,::

      end................ : 2020-04-16 20:31:49 | was: 2020-04-16 20:33:27 <now>
                            -------------------

    (where the "was" time continues to show the current "now" time).

- Finally, you can use either of the 1-minute end time nudge commands
  (described later) to set the end time to now.

  - Pressing ``[`` or ``]``, as described in the next section, will
    usually decrement or increment the end time by one minute, respectively.

    But if the command is used on the active Fact, it'll just set the end
    time to "now".

    So basically you just press ``[`` or ``]`` on the active Fact, and its
    end time will be set to now.

After stopping the active Fact by setting its end time,
you can press ``right`` to go to what's called a gap Fact.

- The new gap Fact will start when the last Fact ended, and its
  end time will not be set -- so it's end time will show ``<now>``.

- If you want to save the new gap Fact, just edit it. If you edit
  anything — set the Activity, apply Tags, edit the description,
  or set the end time — the Fact can then be saved.

===================
Add and Remove time
===================

1 minute of time
----------------

There are four commands to add and subtract time from the start and end times.

- Use ``[`` or ``]`` to subtract or add one minute to the end time, respectively.

- Press ``,`` or ``.`` to subtract or add one minute to the start time, respectively.

5 minutes of time
-----------------

How about 5 minutes? ``Shift``-press any of the 1-minute nudge commands
(at least on an English keyboard) to add or subtract 5 minutes instead.

- Press ``{`` or ``}`` to decrement or increment the end time by 5 minutes.

- Press ``<`` or ``>`` to decrement or increment the start time by 5 minutes.

Any minutes of time
-------------------

dob supports a Vim-like [count] prefix to the nudge time commands.

Type an amount of time, in minutes, before the nudge command.

- For instance, press ``7.5[`` to remove 7.5 minutes from the end time.

- Or, e.g., type ``30.`` to add 30 minutes to the start.

Nudging both start and end
--------------------------

To nudge both the start time and end time forward by one minute, press
``Ctrl-Shitf-right``.

To decrement both the start and end times by one minute, press
``Ctrl-Shift-left``.

=====================
Set time by reference
=====================

You can also specify the start or end time relative to the other time.

This is useful if you want to exactly set the duration of a Fact,
for example, you want the Fact to be exactly one hour long.

To use this feature, press either plus ``+`` or minus ``-``,
followed by a number of minutes,
and then press ``Enter``, ``Tab``, or ``m``.

Start the command with ``+`` to set the end time relative to the start time.

Or start the command with ``-`` to set the start time relative to the end time.

- For example, if you want the current Fact to end 30 minutes after it
  started, type ``+30<Enter>`` (or ``+30<Tab>``, or ``+30m``).

To set the start time relative to the end time, use the minus sign, ``-``.

- For example, to set the start time two a half minutes before the end,
  type ``-2.5<Enter>``.

To use hours instead, terminate the command with ``h``.

- For example, to set the end 90 minutes after the start,
  you could type ``+1.5h``.

=============================
Whether to leave a gap or not
=============================

When you edit a Fact's start time forward, or its end time backward,
you can choose whether a neighboring Fact's time is also adjusted,
or whether a gap should be left in its place.

- Type an exclamation mark, ``!``, before of after the number prefix
  to have dob leave a gap (i.e., dob will not edit the neighboring
  Fact).

  Otherwise dob will edit the neighbor's start or end time to stay
  the same as the current Fact's end or start time.

- For instance, suppose Fact A starts at 12:00 and ends at 13:00,
  and Fact B starts at 13:00 and ends at 14:00. If Fact B is the
  current Fact — it's the Fact showing in the editor — if you
  type ``-15!<Enter>`` (or ``!-15<Enter>``), dob will change the
  Fact B start time from 13:00 to 13:45, and it will not edit
  Fact A.

  However, without the ``!``, e.g., ``-15<Enter>``, dob changes
  the Fact B start time from 13:00 to 13:45, and it also changes
  the Fact A end time from 13:00 to 13:45.

- You can also use the ``!`` gap-indicator with the time nudging
  commands, e.g., ``10!,`` or ``!10,`` will add ten minutes to
  the current Fact's start time, and it will *not* change the
  end time of the Fact before it.

You've reached the end of the interactive editor documentation!

Thanks for learning dob!!

