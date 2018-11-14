from random import seed

import pytest

from django.core import serializers
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from collab_canvas.users.models import User


@pytest.mark.django_db
class BaseVisualTest(TestCase):

    """Base inheritable class to cover atomic tests with canvas creation."""

    BASE_SEED = seed(3141592)

    def setUp(self):
        self.super_user = User.objects.create_superuser(username="test_super",
                                                        email="test@test.com",
                                                        password="secret")


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
