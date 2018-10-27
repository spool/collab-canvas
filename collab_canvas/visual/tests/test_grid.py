from datetime import timedelta

from django.utils import timezone

from ..models import VisualCanvas  # , CELL_NEIGHBOURS
from .utils import BaseVisualCanvasTest


class TestTorusGrid(BaseVisualCanvasTest):

    """Test initiating a VisualCanvas"""

    def test_creating_2x2torus(self):
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


class TestNonTorusGrid(BaseVisualCanvasTest):

    """
    Test generating a grid that isn't a torus.

    Crucially, these edge cells never have a full grid of neighbours.
    """

    def test_non_grid(self):
        """Test creation a non-grid canvas."""
        canvas = VisualCanvas.objects.create(
            title='Test Non-Grid',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=2,
            creator=self.super_user,
            is_torus=False
        )
        self.assertEqual(canvas.visual_cells.count(), 4)

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
