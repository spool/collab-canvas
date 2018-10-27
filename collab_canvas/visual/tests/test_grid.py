from datetime import timedelta

from django.utils import timezone

from ..models import VisualCanvas  # , CELL_NEIGHBOURS
from .utils import BaseVisualCanvasTest


class TestTorusGrid(BaseVisualCanvasTest):

    """Test initiating a VisualCanvas"""

    def test_creating_3x3_torus(self):
        """Test basic creation of a torus."""
        CORRECT_CELL_NEIGHBOURS = {
            (0, 0): {'north': (0, 1), 'north_east': (1, 1),
                     'east': (1, 0), 'south_east': (1, 2),
                     'south': (0, 2), 'south_west': (2, 2),
                     'west': (2, 0), 'north_west': (2, 1)},
            (1, 0): {'north': (1, 1), 'north_east': (2, 1),
                     'east': (2, 0), 'south_east': (2, 2),
                     'south': (1, 2), 'south_west': (0, 2),
                     'west': (0, 0), 'north_west': (0, 1)},
            (2, 0): {'north': (2, 1), 'north_east': (0, 1),
                     'east': (0, 0), 'south_east': (0, 2),
                     'south': (2, 2), 'south_west': (1, 2),
                     'west': (1, 0), 'north_west': (1, 1)},
            (0, 1): {'north': (0, 2), 'north_east': (1, 2),
                     'east': (1, 1), 'south_east': (1, 0),
                     'south': (0, 0), 'south_west': (2, 0),
                     'west': (2, 1), 'north_west': (2, 2)},
            (1, 1): {'north': (1, 2), 'north_east': (2, 2),
                     'east': (2, 1), 'south_east': (2, 0),
                     'south': (1, 0), 'south_west': (0, 0),
                     'west': (0, 1), 'north_west': (0, 2)},
            (2, 1): {'north': (2, 2), 'north_east': (0, 2),
                     'east': (0, 1), 'south_east': (0, 0),
                     'south': (2, 0), 'south_west': (1, 0),
                     'west': (1, 1), 'north_west': (1, 2)},
            (0, 2): {'north': (0, 0), 'north_east': (1, 0),
                     'east': (1, 2), 'south_east': (1, 1),
                     'south': (0, 1), 'south_west': (2, 1),
                     'west': (2, 2), 'north_west': (2, 0)},
            (1, 2): {'north': (1, 0), 'north_east': (2, 0),
                     'east': (2, 2), 'south_east': (2, 1),
                     'south': (1, 1), 'south_west': (0, 1),
                     'west': (0, 2), 'north_west': (0, 0)},
            (2, 2): {'north': (2, 0), 'north_east': (0, 0),
                     'east': (0, 2), 'south_east': (0, 1),
                     'south': (2, 1), 'south_west': (1, 1),
                     'west': (1, 2), 'north_west': (1, 0)},
        }
        canvas = VisualCanvas.objects.create(
            title='Test Torus',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=3,
            creator=self.super_user,
            is_torus=True
        )
        self.assertEqual(canvas.visual_cells.count(), 9)
        for cell in canvas.visual_cells.order_by('x_position', 'y_position'):
            with self.subTest(cell=cell):
                self.assertEqual(cell.get_neighbours(as_tuple=True),
                                 CORRECT_CELL_NEIGHBOURS[cell.coordinates])


class TestNonTorusGrid(BaseVisualCanvasTest):

    """
    Test generating a grid that isn't a torus.

    Crucially, these edge cells never have a full grid of neighbours.
    """

    def test_not_tuple_grid(self):
        """Test creation a non-grid canvas."""
        CORRECT_CELL_NEIGHBOURS = {
            (0, 0): {'north': (0, 1), 'north_east': (1, 1),
                     'east': (1, 0), 'south_east': None,
                     'south': None, 'south_west': None,
                     'west': None, 'north_west': None},
            (1, 0): {'north': (1, 1), 'north_east': None,
                     'east': None, 'south_east': None,
                     'south': None, 'south_west': None,
                     'west': (0, 0), 'north_west': (0, 1)},
            (0, 1): {'north': None, 'north_east': None,
                     'east': (1, 1), 'south_east': (1, 0),
                     'south': (0, 0), 'south_west': None,
                     'west': None, 'north_west': None},
            (1, 1): {'north': None, 'north_east': None,
                     'east': None, 'south_east': None,
                     'south': (1, 0), 'south_west': (0, 0),
                     'west': (0, 1), 'north_west': None},
        }
        canvas = VisualCanvas.objects.create(
            title='Test Non-Grid',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=2,
            creator=self.super_user,
            is_torus=False
        )
        self.assertEqual(canvas.visual_cells.count(), 4)
        for cell in canvas.visual_cells.order_by('x_position', 'y_position'):
            with self.subTest(cell=cell):
                self.assertEqual(cell.get_neighbours(as_tuple=True),
                                 CORRECT_CELL_NEIGHBOURS[cell.coordinates])

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
