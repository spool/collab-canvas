from datetime import timedelta

from django.utils import timezone

from factory import LazyAttribute, LazyFunction, Sequence, SubFactory
from factory.django import DjangoModelFactory

import pytest

from random import seed

from django.core import serializers
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from collab_canvas.users.models import User
from collab_canvas.visual.models import VisualCanvas


BASE_SEED = seed(3141592)


class SuperUser(DjangoModelFactory):

    """Inherits from UserFactor to add Superuser privilages."""

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
                                'new_cells_allowed')

    title = 'Test Non-Torus Grid'
    start_time = LazyFunction(timezone.now)
    end_time = LazyAttribute(lambda c: c.start_time + timedelta(seconds=600))
    grid_height = 2
    grid_width = 2
    creator = SubFactory(SuperUser)
    new_cells_allowed = False
    is_torus = False


@pytest.mark.django_db
class BaseVisualTest(TestCase):

    """Base inheritable class to cover atomic tests with canvas creation."""

    def setUp(self):
        UserFactory.reset_sequence()
        seed(3141592)


@pytest.mark.django_db
class BaseTransactionVisualTest(TestCase):

    """Base inheritable class which can also handle transactions/rollbacks."""

    def setUp(self):
        self.super_user = User.objects.create_superuser(username="test_super",
                                                        email="test@test.com",
                                                        password="secret")
        self.anonymous_user = AnonymousUser()
        self.requests = RequestFactory


def dump_data(query_sets, file_format="json", indent=2):
    """
    A quick way to add a datadump to run during tests to create a fixuture.

    Avoids polluting the database with extra ids.
    """
    JSONSerializer = serializers.get_serializer(file_format)
    json_serializer = JSONSerializer()
    with open("fixture_dump.json", "w") as dump_file:
        json_serializer.serialize(query_sets, stream=dump_file, indent=indent)
