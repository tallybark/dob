# -*- coding: utf-8 -*-

# This file is part of 'hamster_cli'.
#
# 'hamster_cli' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster_cli' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster_cli'.  If not, see <http://www.gnu.org/licenses/>.

"""Factories to provide easy to use randomized instances of our main objects."""

import datetime

import factory
import faker
import hamster_lib


class CategoryFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Category`` instances."""

    pk = None
    name = factory.Faker('word')

    class Meta:
        model = hamster_lib.Category


class ActivityFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Activity`` instances."""

    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = hamster_lib.Activity


class FactFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Fact`` instances."""

    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = hamster_lib.Fact
