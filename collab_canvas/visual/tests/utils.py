import pytest

from django.test import TestCase, RequestFactory

from collab_canvas.users.models import User


@pytest.mark.django_db
class BaseVisualCanvasTest(TestCase):

    """Base pattern for inheritance."""

    def setUp(self):
        self.super_user = User.objects.create_superuser(username="test_super",
                                                        email="test@test.com",
                                                        password="secret")
        self.user = User.objects.create_user(username="test_user",
                                             email="test@test.com",
                                             password="secret")
        self.factory = RequestFactory()
