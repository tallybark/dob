#############
Configure dob
#############

Before we dive into dob and how to really use it, you'll first want to understand
how to configure it.

dob has a robust user configuration. There are lots of settings you can tweak,
and there are lots of ways to tweak those settings (like using the CLI,
editing a config file, or even setting environment variables).

Let's start with how to view the config. You can either dump it to the
terminal using the CLI, or you can open the config file.

We recommend using the CLI to see all the settings. The config file may not
contain settings that have not been changed from their default.

===============
Dump the config
===============

Run the ``config dump`` command to see all the settings you can change.

For example::

  $ dob config dump
  +---------+----------+-------------------------------+------------------------------+
  | Section |   Name   |        Value <Default>        |             Help             |
  +=========+==========+===============================+==============================+
  |      db | orm      | sqlalchemy                    | ORM used by dob to interface |
  |         |          |                               | with the DBMS. Most likely   |
  |         |          |                               | ‘sqlalchemy’.                |
  +---------+----------+-------------------------------+------------------------------+
  |      db | engine   | sqlite                        | Database management system   |
  |         |          |                               | used to manage your data.    |
  |         |          |                               | Most likely ‘sqlite’.        |
  ...

You'll notice that each config setting belongs to a section, has a name, has a
current value (with the default value shown in <brackets> if different), and
a bit of help.

=====================
Dump a config section
=====================

You can restrict the dump to a section or even a specific setting by specifying
them after the command. E.g.,::

  $ dob config dump term
  +---------+---------------+-----------------+---------------------------------------+
  | Section |     Name      | Value <Default> |                 Help                  |
  +=========+===============+=================+=======================================+
  |    term | editor_suffix | .rst <>         | The filename suffix to tell EDITOR so |
  |         |               |                 | it can determine highlighting         |
  ...

=====================
Dump a single setting
=====================

Or, to see a single setting's entry, include the setting name::

  $ dob config dump term use_color
  +---------+-----------+-----------------+-------------------------------------------+
  | Section |   Name    | Value <Default> |                   Help                    |
  +=========+===========+=================+===========================================+
  |    term | use_color | True            | If True, use color and font ornamentation |
  |         |           |                 | in output.                                |
  +---------+-----------+-----------------+-------------------------------------------+

===========================
Get and set config settings
===========================

If you'd like to see just the value, use the ``get`` command. For instance::

  $ dob config get editor centered
  True

To change the value of a setting, use the ``set`` command. For instance::

  $ dob config set editor centered False
  $ dob config get editor centered
  False

You can also edit config settings directly in the config file itself.

=====================
Find your config file
=====================

If you'd like to inspect the raw config file, you'll have to find where it lives.

Run the ``details`` command, e.g.,::

  $ dob details
  You are running dob version 3.0.7
  Configuration file at: /home/user/.config/dob/dob.conf
  Plugins directory at: /home/user/.config/dob/plugins
  Logfile stored at: /home/user/.cache/dob/log/dob.log
  Reports exported to: .{format}
  Using sqlite on database: /home/user/.local/share/dob/dob.sqlite

Obviously, you'll find the config at the path shown after "Configuration file at".

- If you really want to impress yourself, you can automate opening the config.
  Run the ``environs`` command to output shell-style ``VAR=VALUE`` strings,
  source that, and use the ``DOB_CONF`` variable, e.g.,::

    $ eval "$(dob env)" && vim $DOB_CONF

- If you'd like to keep the config file under revision control, feel free
  to use a symlink at the config file path, and then put the real file in
  your private repo.

==========================
Change settings at runtime
==========================

If you want to change configuration settings on the fly, you can do that, too.

- You can specify a different configuration file using the ``DOB_CONFIGFILE``
  variable. You could set it permanently, say, from your startup scripts,
  or you could set if just for a single command, e.g.,::

    DOB_CONFIGFILE=path/to/dob.conf dob COMMAND ...

- Likewise, you can specify config values using environment variables, e.g.,::

    DOB_CONFIG_DB_ENGINE=sqlite dob stats

  or using a global CLI option, ``-c``, e.g.,::

    dob -c db.engine=sqlite stats

Refer to ``dob config --help`` for more details.

