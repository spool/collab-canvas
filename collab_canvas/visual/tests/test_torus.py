from unittest import skip

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from .utils import BaseVisualTest, CanvasFactory, UserFactory


class TestCreatingTorusGrid(BaseVisualTest):

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
        canvas = CanvasFactory(
            title='Test Torus',
            grid_height=3,
            grid_width=3,
            is_torus=True
        )
        self.assertEqual(canvas.visual_cells.count(), 9)
        for cell in canvas.visual_cells.order_by('x_position', 'y_position'):
            with self.subTest(cell=cell):
                self.assertEqual(cell.get_neighbours(as_tuple=True),
                                 CORRECT_CELL_NEIGHBOURS[cell.coordinates])
        with self.subTest("Test invalidly altering the height of the canvas."):
            canvas.grid_height = 4
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    canvas.generate_grid(add=True)
                self.assertIn("Cells cannot be added to a torus that already "
                              "has 9 cells", str(error.exception))

    def test_creating_2x2_torus(self):
        """Test creating a 2x2 torus."""
        with transaction.atomic():
            with self.assertRaises(ValidationError) as error:
                canvas = CanvasFactory(
                    title='Test Torus',
                    grid_height=2,
                    grid_width=2,
                    is_torus=True
                )
                canvas.save()
            self.assertIn('Width 2 < 3 and/or length 2 < 3',
                          str(error.exception))

    @skip("Not yet implemented")
    def test_creating_1x1_torus(self):
        """Test creating a 1x1 torus."""
        pass


class TestTorusGridUsage(BaseVisualTest):

    """Test Torus grid editing."""

    # fixtures = ['base_3x3_torus.json']

    def setUp(self):
        """Add custom initiation for Torus base 3x3 case."""
        super().setUp()
        self.canvas = CanvasFactory(
            title='Test Editing Torus',
            grid_height=3,
            grid_width=3,
            is_torus=True
        )

    def test_fill_torus_canvas_from_centre(self):
        """Test a cell assignments, including preventing a duo assignment."""
        CORRECT_CELL_ARTISTS = {
            (0, 0): 'test7',
            (0, 1): 'test3',
            (0, 2): 'test8',
            (1, 0): 'test1',
            (1, 1): 'test0',
            (1, 2): 'test5',
            (2, 0): 'test2',
            (2, 1): 'test4',
            (2, 2): 'test6',
        }
        users = [UserFactory() for i in range(9)]
        for user in users:
            if user.username == 'test9':  # Test when all cells are allocated
                with self.subTest('Test grid allocation exception'):
                    with transaction.atomic():
                        with self.assertRaises(self.canvas.FullGridException):
                            cell = self.canvas.get_or_create_contiguous_cell()
            else:
                cell = self.canvas.get_or_create_contiguous_cell()
                cell.artist = user
                cell.save()
        for cell_coordinates, username in CORRECT_CELL_ARTISTS.items():
            with self.subTest(f"Check cell {cell_coordinates} has correct owner "
                              f"{username}.",
                              cell_coordinates=cell_coordinates,
                              username=username):
                cell = self.canvas.visual_cells.get(x_position=cell_coordinates[0],
                                                    y_position=cell_coordinates[1])
                self.assertEqual(cell.artist.username, username)

    def test_unique_artist_per_canvas(self):
        """Test enforcing uniquen users per canvas."""
        user = UserFactory()
        cell = self.canvas.get_or_create_contiguous_cell()
        self.assertEqual(cell.coordinates, (1, 1))
        cell.artist = user
        cell.save()
        cell2 = self.canvas.get_or_create_contiguous_cell()
        cell2.artist = user
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                cell2.save()
        self.assertNotIn(cell2, user.visual_cells.all())
