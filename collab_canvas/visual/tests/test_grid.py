from datetime import timedelta

from random import seed

from unittest import skip

from django.utils import timezone

from ..models import VisualCanvas
from .utils import BaseCreateVisualCanvasTest, BaseVisualCanvasUserTest


seed(3141592)


class TestCreatingTorusGrid(BaseCreateVisualCanvasTest):

    """
    Test initiating a VisualCanvas

    Todo:
        * Fix 2x2 and 1x1 options or enforce minimum 3x3.
    """

    def test_creating_3x3_torus(self):
        """Test basic creation of a 3x3 torus."""
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

    @skip("Not yet implemented")
    def test_creating_2x2_torus(self):
        """Test creating a 2x2 torus."""
        pass

    @skip("Not yet implemented")
    def test_creating_1x2_torus(self):
        """Test creating a 2x2 torus."""
        pass


class TestTorusGridUsage(BaseVisualCanvasUserTest):

    """Test Torus grid editing."""

    # fixtures = ['base_3x3_torus.json']

    def setUp(self):
        """Add custom initiation for Torus base 3x3 case."""
        super().setUp()
        self.canvas = VisualCanvas.objects.create(
            title='Test Editing Torus',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=20),
            grid_length=3,
            creator=self.super_user,
            is_torus=True
        )

    def test_get_centre_cell(self):
        """Test getting centre cell."""
        self.assertEqual(self.canvas.get_centre_cell_coordinates(), (1, 1))

    def test_get_random_cell_coordinates(self):
        """Test getting a random cell within the torus."""
        self.assertEqual(self.canvas.get_random_cell_coordinates(), (2, 2))

    def test_get_central_initial_cell(self):
        """Test assigning cell to a user."""
        cell = self.canvas.get_or_create_contiguous_cell()
        self.assertEqual(cell.coordinates, (1, 1))

    def test_get_random_initial_cell(self):
        """Test assigning cell to a user."""
        cell = self.canvas.get_or_create_contiguous_cell(
            first_cell_algorithm='random')
        self.assertEqual(cell.coordinates, (0, 1))


class TestNonTorusGrid(BaseCreateVisualCanvasTest):

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
