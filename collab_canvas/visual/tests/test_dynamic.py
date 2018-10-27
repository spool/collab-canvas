from datetime import timedelta

from django.utils import timezone

from ..models import VisualCanvas  # , CELL_NEIGHBOURS
from .utils import BaseVisualCanvasTest


class TestGeneratingEmptyCanvas(BaseVisualCanvasTest):

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
            grid_length=0,
            creator=self.super_user,
            is_torus=False
        )
        self.assertEqual(canvas.visual_cells.count(), 0)
