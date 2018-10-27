from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.utils import timezone

import pytest

from collab_canvas.users.models import User

from ..models import VisualCanvas  # , CELL_NEIGHBOURS


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

    def test_creating_torus(self):
        """Test basic creation of a torus."""
        canvas = VisualCanvas.objects.create(
            title='Test Torus',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=2,
            creator=self.super_user,
            is_torus=True
        )
        self.assertEqual(canvas.visual_cells.count(), 4)
        # self.subTest()
        # for cell in canvas.visual_cells.order_by('x_position', 'y_position'):
        #     with self.subTest(cell=cell):

        # with self
        # test_cell = canvas.objects.get(x_position=1, y_position=0)
        # self.assertEqual(test_cell.get_neighbours(),

    def test_non_grid(self):
        """Test creation a non-grid canvas."""
        canvas = VisualCanvas.objects.create(
            title='Test Non-Grid',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=0,
            creator=self.super_user,
            is_torus=False
        )
        self.assertEqual(canvas.visual_cells.count(), 0)

    # def test_creating_grid_permission(self):
    #     try:
    #         canvas = VisualCanvas.objects.create(
    #             title='Test Canvas',
    #             start_time=datetime.now(),
    #             end_time=datetime.now() + timedelta(seconds=20),
    #             grid_length=2,
    #             creator=self.user,
    #             is_torus=True
    #         )
    #     except VisualCanvas.PermissionError:
    #         self.assertEqual(canvas.visual_cells.count(), 7)
    #     assert False
