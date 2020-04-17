########
Concepts
########

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |hamster-cli| replace:: ``hamster-cli``
.. _hamster-cli: https://github.com/projecthamster/hamster-cli

This is a high-level, very general overview of basic |dob|_ concepts.

(These concepts are essentially the same as those in
`Legacy Hamster <https://github.com/projecthamster/hamster>`__.)

Fact
   The essence of |dob|_ is the *Fact*, an interval of time having a start
   time and almost always having an end time (except for the *active Fact*).
   A Fact may also be associated with a specific *Activity*,
   which itself is associated with a specific *Category*.
   Facts may have zero or more *Tags* assigned to them.
   Also, a Fact has a *Description*.

   Note that no two Facts may occupy the same *time window*.
   Specifically, the start-to-end times of two separate Facts
   may not overlap.

Factoid
   A *Factoid* is a string representation of a Fact. It can be parsed
   to create a new Fact instance, and it can contain any of the following:
   A start time, an end time, an Activity, a Category, zero or more Tags,
   and a description of the Fact.

   - A simple Factoid might look like:

     ``from 2020-04-01 10:00 to 12:00: Activity@Category: #tag1 #tag2: Description."``

Activity
   An *Activity* generally describes what occurred during the time
   interval captured by the Fact.

   For instance, the user might choose to use "Meeting" and
   "Coffee break", among other names, for their Activities.

Category
   A *Category* describes a collection of Activities.

   Categories allow the user to reuse the same Activity name (by using
   different Category names). Also, Categories allow the user to group
   Activities, which could be useful for reporting and other features.

   For instance, the user might choose to use "Work" and "Personal",
   among other names, for their Activities' Categories.

Act\@Gory
   An *Act@Gory* (pronounced "act-eh-gory") is a documentation construct
   for the combined Activity and Category names for a given Fact. It is
   so-called because the ``dob`` CLI parser expects the user to specify
   the activity with the *at* (``@``) symbol.
   For instance, in the following Factoid,
   ``at 08:00: Meeting@Work: I wish I was outside.``,
   the Act\@Gory is ``Meeting@Work`` (where ``Meeting`` is
   the Activity and ``Work`` is the Category, naturally).

Tag
   A *Tag* is another way to label a Fact other than using an Act\@Gory.

   A Tag is simply a string associated with a Fact.

   The user can apply more than one Tag to any Fact.

   Tags are not associated with any specific Activity or Category.

Musings on Metadata
   You might ask, *How do I know when to use an Activity, or when to use a Tag?*

   Essentially, at its core, a Tag is the same construct as an Act\@Gory:
   It's simply a string associated with a Fact.

   As such, a decent end user application will, for instance, enable the user
   to search for Facts using Tag names just as easily as it will allow the
   user to search for Facts using Act\@Gory names.

   Really, what it boils down to is user preference.

   - Consider the user who works on a different project every day.

     Would the user prefer not to use tags, but to use a new Activity label everyday?
     Or would the user prefer to use the same Activity label every day, and to specify
     a new Tag name every day instead?

     *The answer:* It's up to the user! Either approach works fine.
     But the application experience will be slightly different
     between the two approaches.

Active Fact
   An *active* Fact has no end time, and its start time is set later
   than all other Facts' end times, except maybe the penultimate Fact.

   There can be at most one active Fact in the data store, and,
   if it exists, it is the latest Fact chronologically.

   - In Legacy Hamster, the user could save any Fact without an end time.
     And sometimes the application did so by accident.
     But having more than one unclosed Fact wreaks havoc when trying to do
     interesting things with the data, such as generating reports, or compiling
     statistics. As such, |dob|_ imposes a limit of one such open-ended Fact.
     Also, when upgrading a legacy database, |dob|_ will close any open Facts
     it finds (making them *momentaneous* instead, discussed next).

     - An "active" Fact might also be considered "endless" or "ongoing",
       but an *endless* or *ongoing* Fact is not necessarily the *active* Fact.

       An endless or ongoing Fact simply does not have an end time, and
       in legacy Hamster, there could be many of these. But there can be
       only one active Fact, whose end time will be unset, and whose start
       time will either be "now" or earlier than "now".

Momentaneous Fact
   A *momentaneous* Fact is a Fact whose start time is the same as its end time.

   Such a feature may seem a bit contrived, but it's necessary to handle some
   bugs in Legacy Hamster. It also allows the user to make multiple Facts at
   the same time without violating the no-2-Facts-may-overlap rule, which could
   be a handy trick for creating different Facts at the same time, but using
   different Act\@Gories and Tags.

