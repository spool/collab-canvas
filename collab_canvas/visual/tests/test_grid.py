from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from ..models import VisualCell
from .utils import BaseVisualTest, CanvasFactory, UserFactory


class TestCellAllocation3x3NonTorusGrid(BaseVisualTest):

    """Test basic cell allocation."""

    def setUp(self):
        """Create base initialised 3x3 grid for testing."""
        super().setUp()
        self.canvas = CanvasFactory(
            grid_height=3,
            grid_width=3,
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
        """Test get_or_create_contiguous_cell() assignment of random cell."""
        cell = self.canvas.get_or_create_contiguous_cell(
            first_cell_algorithm='random')
        self.assertEqual(cell.coordinates, (2, 2))


class TestNonTorus2x2Grid(BaseVisualTest):

    """
    Test generating a grid that isn't a torus.

    Crucially, these edge cells never have a full grid of neighbours.
    """

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

    def setUp(self):
        """Create base initialised grid for testing."""
        super().setUp()
        self.canvas = CanvasFactory()

    def test_invalid_start_end_times(self):
        """Setting an end_time < start_time cannot be saved."""
        self.canvas.end_time = self.canvas.start_time - timedelta(seconds=10)
        with self.assertRaises(ValidationError) as error:
            self.canvas.save()
        self.assertIn((f'start_time {self.canvas.start_time} must be earlier '
                       f'than end_time {self.canvas.end_time}'),
                      str(error.exception))

    def test_non_torus_grid(self):
        """Test creation a non-grid canvas."""
        self.assertEqual(self.canvas.visual_cells.count(), 4)
        for cell in self.canvas.visual_cells.order_by('x_position',
                                                      'y_position'):
            with self.subTest(f"Check {cell} for correct neighbours",
                              cell=cell):
                self.assertEqual(
                    cell.get_neighbours(as_tuple=True,
                                        include_null_neighbours=True),
                    self.CORRECT_CELL_NEIGHBOURS[cell.coordinates])

    def test_unique_cell_coordinates_per_canvas(self):
        """
        Duplicate cells on a canvas should raise an integrity error.

        Todo:
            * This should also consider tests where the canvas can be edited
            but uniqueness is still enforced.
        """
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                bad_cell = VisualCell(x_position=0, y_position=0,
                                      canvas=self.canvas)
                bad_cell.save()

    def test_canvas_full(self):
        """Test filling canvas and preventing any furter cell assignments."""
        CORRECT_CELL_ARTISTS = {
            (0, 0): 'test0',
            (0, 1): 'test1',
            (1, 0): 'test3',
            (1, 1): 'test2',
        }
        users = [UserFactory() for i in range(5)]  # Sequence will cover 1-5
        for user in users:
            if user.username == 'test4':  # Test when all cells are allocated
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

    def test_no_cells_can_be_added_outside_the_grid(self):
        """Test all ways cells outside crid should raise ValidationError."""
        with self.subTest("Both coordinates > than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=7, y_position=7,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (7, 7) is outside the grid',
                              str(error.exception))
        with self.subTest("y_position > than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=0, y_position=7,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (0, 7) is outside the grid',
                              str(error.exception))
        with self.subTest("x_position > than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=7, y_position=0,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (7, 0) is outside the grid',
                              str(error.exception))
        with self.subTest("x_position < than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=-1, y_position=0,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (-1, 0) is outside the grid',
                              str(error.exception))
        with self.subTest("y_position < than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=0, y_position=-1,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (0, -1) is outside the grid',
                              str(error.exception))
        with self.subTest("Both coordinates < than canvas"):
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    bad_cell = VisualCell(x_position=-1, y_position=-1,
                                          canvas=self.canvas)
                    bad_cell.full_clean()
                self.assertIn('Cell position (-1, -1) is outside the grid',
                              str(error.exception))

    def test_modifying_width_and_height(self):
        """Test adding width and height and failures."""
        with self.subTest("Demonstrate failure in changing width without "
                          "can_add=True"):
            self.canvas.grid_width = 3
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    self.canvas.generate_grid()
                self.assertIn("Cells can only be added to a grid if "
                              "can_add=True",
                              str(error.exception))
        with self.subTest("Demonstrate correct width increase with "
                          "can_add=True"):
            with transaction.atomic():
                self.canvas.generate_grid(can_add=True)
                self.assertEqual(self.canvas.max_coordinates, (2, 1))
                self.assertEqual(self.canvas.visual_cells.count(), 6)
        with self.subTest("Demonstrate correct heigh increase with "
                          "can_add=True"):
            self.canvas.grid_height = 4
            with transaction.atomic():
                self.canvas.generate_grid(can_add=True)
                self.assertEqual(self.canvas.max_coordinates, (2, 3))
                self.assertEqual(self.canvas.visual_cells.count(), 12)
        with self.subTest("Raise error if trying to reduce height."):
            self.canvas.grid_height = 2
            with transaction.atomic():
                with self.assertRaises(ValidationError) as error:
                    self.canvas.generate_grid(can_add=True)
                self.assertIn("Cannot add to grid unless both previous "
                              "grid max_coordinates (2, 3) are < "
                              "set max_coordinates (2, 1) for canvas "
                              "Test Non-Torus Grid",
                              str(error.exception))
