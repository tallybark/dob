# This file exists within 'dob-bright':
#
#   https://github.com/hotoffthehamster/dob-bright
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

import pytest

from unittest.mock import PropertyMock

from nark.tests.conftest import *  # noqa: F401, F403
from nark.tests.backends.sqlalchemy.conftest import *  # noqa: F401, F403

from nark.backends.sqlalchemy import objects
from nark.backends.sqlalchemy import storage
from nark.backends.sqlalchemy.managers.migrate import MigrationsManager
from nark.control import NarkControl

from dob_bright.config.urable import ConfigUrable

# (lb): Note that setting pytest_plugins = (...) won't work from this file
# (because not a conftest.py module, I'd guess). One options is to *-import
# necessary files, e.g.,
#   from nark.tests.backends.sqlalchemy.conftest import *  # noqa: F401, F403
# Another option is to add the necessary fixture modules to the pytest_plugins
# list in this directory's conftest.py file, which seems like the better option.
# - tl;dr: Use pytest_plugins, not import, to source additional fixtures.


@pytest.fixture
def dob_runner(alchemy_store, test_fact_cls, controller, mocker, runner):
    """Provide a convenient fixture for running CLI commands against inited dob."""

    # Get the SQLAlchemy Engine() created by alchemy_store,
    # and stashed in the Alchemy MetaData() class maintained
    # by the nark.backends.sqlalchemy.objects module.
    engine = objects.metadata.bind

    # Add the migration version, otherwise dob will complain db not ready.
    migrations = MigrationsManager(alchemy_store)
    migrations.control(version=None, engine=engine)

    mocker.patch.object(
        storage.SQLAlchemyStore, 'create_storage_engine', return_value=engine,
    )

    mocker.patch.object(NarkControl, '_get_store', return_value=alchemy_store)

    mocker.patch.object(
        ConfigUrable, 'config_root', return_value=controller.config,
        new_callable=PropertyMock,
    )

    cfgfile_exists = True
    mocker.patch.object(
        ConfigUrable, 'load_configfile', return_value=cfgfile_exists,
    )

    return runner

