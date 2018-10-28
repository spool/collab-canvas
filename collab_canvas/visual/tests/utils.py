import pytest

from django.core import serializers
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from collab_canvas.users.models import User


@pytest.mark.django_db
class BaseCreateVisualCanvasTest(TestCase):

    """Base inheritable class for testing initializing blank canvas."""

    def setUp(self):
        self.super_user = User.objects.create_superuser(username="test_super",
                                                        email="test@test.com",
                                                        password="secret")


class BaseVisualCanvasUserTest(BaseCreateVisualCanvasTest):

    """Base inheritable class for testing user interaction."""

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="test_user",
                                             email="test@test.com",
                                             password="secret")
        self.anonymous_user = AnonymousUser()
        self.factory = RequestFactory()


def dump_data(query_sets, file_format="json", indent=2):
    """
    A quick way to add a datadump to run during tests to create a fixuture.

    Avoids polluting the database with extra ids.
    """
    JSONSerializer = serializers.get_serializer(file_format)
    json_serializer = JSONSerializer()
    # data = json_serializer.getvalue()
    with open("fixture_dump.json", "w") as dump_file:
        json_serializer.serialize(query_sets, stream=dump_file, indent=indent)
