from datetime import timedelta

from factory import LazyAttribute, LazyFunction, Sequence, SubFactory
from factory.django import DjangoModelFactory

import pytest

from random import seed

from django.core import serializers
from django.test import TestCase
from django.utils import timezone

from collab_canvas.users.models import User
from collab_canvas.visual.models import VisualCanvas, VisualCell


class SuperUser(DjangoModelFactory):

    """
    Inherits from UserFactory to add Superuser privilages.

    Todo:
        * Ideally replace with just a finer grained user permission
        * Consider https://github.com/django-guardian/django-guardian
    """

    class Meta:

        model = User

    name = 'Test Super User'
    username = 'test_super'
    password = 'secret'
    email = 'super@test.com'
    is_superuser = True


class UserFactory(DjangoModelFactory):

    """Simple base factory for users."""

    class Meta:

        model = User
        django_get_or_create = ('username',)

    username = Sequence(lambda i: f'test{i}')
    name = Sequence(lambda i: f'Test User {i}')
    password = LazyAttribute(lambda u: u.username)
    email = LazyAttribute(lambda u: f'{u.username}@test.com')


class CanvasFactory(DjangoModelFactory):

    """Base Canvas Factory."""

    class Meta:

        model = VisualCanvas
        django_get_or_create = ('title', 'creator', 'is_torus',
                                'new_cells_allowed', 'grid_width',
                                'grid_height', 'cell_width', 'cell_height',)

    title = 'Test Non-Torus Grid'
    start_time = LazyFunction(timezone.now)
    end_time = LazyAttribute(lambda c: c.start_time + timedelta(seconds=600))
    grid_height = 2
    grid_width = 2
    cell_width = 3
    cell_height = 3
    creator = SubFactory(SuperUser)
    new_cells_allowed = False
    is_torus = False


class CellFactory(DjangoModelFactory):

    """Base Cell for (0, 0) to work with dynamic, grid and torus canvases."""

    class Meta:

        model = VisualCell
        django_get_or_create = ('canvas', 'artist', 'x_position', 'y_position',
                                'width', 'height', 'south_east_diagonals',
                                'south_west_diagonals', 'colour_range',
                                'is_editable', 'neighbours_may_edit')

    canvas = SubFactory(CanvasFactory, grid_width=0, grid_height=0)
    artist = SubFactory(UserFactory)
    x_position = 0
    y_position = 0
    width = 3
    height = 3
    south_east_diagonals = 2
    south_west_diagonals = 2
    colour_range = 1
    is_editable = True
    neighbours_may_edit = True


@pytest.mark.django_db
class BaseVisualTest(TestCase):

    """Base inheritable class to cover atomic tests with canvas creation."""

    def setUp(self):
        UserFactory.reset_sequence()
        seed(3141592)


# @pytest.mark.django_db
# class BaseTransactionVisualTest(TestCase):
#
#     """Base inheritable class which can also handle transactions/rollbacks."""
#
#     def setUp(self):
#         self.anonymous_user = AnonymousUser()
#         self.requests = RequestFactory


def dump_data(query_sets, file_format="json", indent=2):
    """
    A quick way to add a datadump to run during tests to create a fixuture.

    Avoids polluting the database with extra ids.
    """
    JSONSerializer = serializers.get_serializer(file_format)
    json_serializer = JSONSerializer()
    with open("fixture_dump.json", "w") as dump_file:
        json_serializer.serialize(query_sets, stream=dump_file, indent=indent)
