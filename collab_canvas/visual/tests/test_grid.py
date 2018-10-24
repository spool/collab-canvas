from datetime import datetime, timedelta

# from django.conf import settings
from collab_canvas.users.models import User
from django.test import TestCase, RequestFactory

import pytest

from ..models import VisualCanvas


@pytest.mark.django_db
class TestGeneratingVisualGrid(TestCase):

    """Test initiating a VisualCanvas"""

    def setUp(self):
        self.super_user = User.objects.create_superuser(username="test_super",
                                                        email="test@test.com",
                                                        password="secret")
        self.user = User.objects.create_user(username="test_user",
                                             email="test@test.com",
                                             password="secret")
        self.factory = RequestFactory()

    def test_creating_grid(self):
        """Test basic creation of a grid."""
        canvas = VisualCanvas.objects.create(
            title='Test Canvas',
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=20),
            grid_length=2,
            creator=self.super_user,
            is_torus=True
        )
        self.assertEqual(canvas.visual_cells.count(), 4)
