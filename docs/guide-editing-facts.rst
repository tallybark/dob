#######################
Edit Facts and Metadata
#######################

Each Fact has 6 attributes you can edit:

- Start time.

- End time.

- Activity.

- Category.

- Tags.

- Description.

You can specify the start and end time directly in the editor using a
text input, described next, or you can edit time using special "nudge"
commands, described in a later section.

You can change the Activity, Category, and Tags using the Awesome Prompt.

Finally, you can edit the description using your normal text editor, as
previously described.

============================
Edit Start Time and End Time
============================

When dob starts, it starts with focus on the description area -- you should
see a blocky white cursor in the upper-left of the description box.

You can run most dob commands from this "mode", but you can also change focus
to the start time and end time controls to directly edit those values.

To edit the start time directly, press ``s`` to focus its control.

- You can also press ``Tab`` or ``Shift-Tab`` to shift focus between
  the start time, end time, and the description.

- When finished editing the start time value, press ``Enter`` to apply
  it, or press ``s`` to toggle away from the control (which also applies
  it), or press ``Tab`` or ``Shift-Tab`` (which also shift focus and apply
  the new time).

You can likewise access the end time control by pressing ``e``, and
editing the end time in a manner similar to editing the start time.

Note that you do not have to enter a complete date and time in the field.
You can enter just the date, or just the time (for today's date), or
even a ``+`` or a ``-`` followed by a delta time to add or remove minutes
from the field's original value.

Directly editing the time value can feel tedious, so dob provides
more convenient ways to change a Fact's start and end time.

- The section `Nudge Start and End Time`__ describes more powerful
  and convenient commands to change time.

__ https://dob.readthedocs.io/en/latest/guide-nudging-time.html

=================================
Edit Activity, Category, and Tags
=================================

The Activity and Category is edited as one unit (colloquially called the "act\@gory").

Press ``a`` to launch the Activity prompt.

- Type the Activity\@Category name, or use auto-complete to fill it in, or
  choose an act\@gory from the drop-down list.

  Press ``Enter`` to accept the Activity and return to dob. Or press
  ``Ctrl-q`` to cancel the prompt without changing the Activity.

- You'll notice there are a number of commands shown in the bottom toolbar.

  - You can press ``Alt-i`` to toggle auto-complete case sensitivity.

  - You can press ``Alt-m`` to toggle whether auto-complete should
    match in the middle of strings, or just at the start.

  - Use the ``F``-keys – ``F2`` through ``F6`` – to change how the drop-down
    list is ordered.

    - Press ``F2`` to order alphabetically, by name.

    - Press ``F3`` to order by start time, i.e., show the
      activities you've applied to recent Facts.

    - Press ``F4`` to order by count, i.e., show the most-used activities.

    - Press ``F5`` to order by time, i.e., show the activities that have the
      most accumulated time spent on them (by adding up all their Facts'
      durations).

    - Press ``F6`` to order by most recently used *in the app* (not to be
      confused with most recently used by any Facts, which ``F3`` shows).

    Each ``F``-key has three states. Pressing the same ``F``-key again will
    cycle through these states: Show the drop-down list sorted normally,
    show the drop-drop sorted in reverse, or hide the dropdown.

You'll also use a special prompt to add and remove Tags.

Press ``t`` to edit Tags.

- You can type a Tag name and press ``Enter`` to add it.

  Or you can start to type a Tag name, and then press ``Tab``
  to choose the auto-complete suggestion, if appropriate.

  Or you can use the arrow keys to select a Tag from the
  drop-down list, followed by ``Enter``.

- When you're done with Tags, press ``Enter`` on an empty input field
  to close the Tags prompt.

  For example, type a Tag name, press ``Enter`` to add it, and then
  press ``Enter`` again to close the prompt.

- To remove a Tag, you can type the Tag name to remove, and press ``Enter``.

  Or, press ``F8`` to view the list of Tags that have been applied,
  and then use the arrows keys to select one from the drop-down list,
  followed by ``Enter`` to remove it.

