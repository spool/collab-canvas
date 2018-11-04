from datetime import timedelta

from random import seed

from unittest import skip

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from collab_canvas.users.models import User
from ..models import VisualCanvas, VisualCell
from .utils import BaseVisualTest, BaseTransactionVisualTest


seed(3141592)


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
    def test_creating_1x1_torus(self):
        """Test creating a 1x1 torus."""
        pass


class TestTorusGridUsage(BaseTransactionVisualTest):

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
        self.user = User.objects.create(name="Test User", email="test@t.com",
                                        password="test")

    def test_get_centre_cell(self):
        """Test getting centre cell."""
        self.assertEqual(self.canvas.get_centre_cell_coordinates(), (1, 1))

    def test_get_random_cell_coordinates(self):
        """Test getting a random cell within the torus."""
        self.assertEqual(self.canvas.get_random_cell_coordinates(), (1, 2))

    def test_get_central_initial_cell(self):
        """Test assigning cell to a user."""
        cell = self.canvas.get_or_create_contiguous_cell()
        self.assertEqual(cell.coordinates, (1, 1))

    def test_get_random_initial_cell(self):
        """Test assigning cell to a user."""
        cell = self.canvas.get_or_create_contiguous_cell(
            first_cell_algorithm='random')
        self.assertEqual(cell.coordinates, (1, 0))

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
        users = [
            User.objects.create(username=f'test{i}', email=f'test{1}@test.com',
                                password=f'test{i}')
            for i in range(9)
        ]
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
        cell = self.canvas.get_or_create_contiguous_cell()
        self.assertEqual(cell.coordinates, (1, 1))
        cell.artist = self.user
        cell.save()
        cell2 = self.canvas.get_or_create_contiguous_cell()
        cell2.artist = self.user
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                cell2.save()
        self.assertNotIn(cell2, self.user.visual_cells.all())


class TestNonTorusGrid(BaseVisualTest):

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
        self.canvas = VisualCanvas.objects.create(
            title='Test Non-Grid',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=600),
            grid_length=2,
            creator=self.super_user,
            is_torus=False
        )

    def test_not_torus_grid(self):
        """Test creation a non-grid canvas."""
        self.assertEqual(self.canvas.visual_cells.count(), 4)
        for cell in self.canvas.visual_cells.order_by('x_position',
                                                      'y_position'):
            with self.subTest("Check each cell for correct neighbours",
                              cell=cell):
                self.assertEqual(cell.get_neighbours(as_tuple=True),
                                 self.CORRECT_CELL_NEIGHBOURS[
                                     cell.coordinates])

    def test_no_duplicate_cells_can_be_added(self):
        """Duplicate cells on a canvas should raise an integrity error."""
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                bad_cell = VisualCell(x_position=0, y_position=0,
                                      canvas=self.canvas)
                bad_cell.save()

    def test_canvas_full(self):
        """Test filling canvas and preventing any furter cell assignments."""
        CORRECT_CELL_ARTISTS = {
            (0, 0): 'test0',
            (0, 1): 'test3',
            (1, 0): 'test1',
            (1, 1): 'test2',
        }
        users = [
            User.objects.create(username=f'test{i}', email=f'test{1}@test.com',
                                password=f'test{i}')
            for i in range(5)
        ]
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
