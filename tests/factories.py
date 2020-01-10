# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.

"""Factories to provide easy to use randomized instances of our main objects."""

import datetime

import factory
import faker

from nark.items import Activity, Category, Fact


class CategoryFactory(factory.Factory):
    """Provide a factory for randomized ``nark.Category`` instances."""

    pk = None
    name = factory.Faker('word')

    class Meta:
        model = Category


class ActivityFactory(factory.Factory):
    """Provide a factory for randomized ``nark.Activity`` instances."""

    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = Activity


class FactFactory(factory.Factory):
    """Provide a factory for randomized ``nark.Fact`` instances."""

    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = Fact

