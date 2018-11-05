from datetime import timedelta

from random import seed

from django.utils import timezone

from ..models import VisualCanvas
from .utils import BaseVisualTest
from collab_canvas.users.models import User


seed(3141592)


class TestGeneratingEmptyCanvas(BaseVisualTest):

    """
    Test generating a grid that isn't a torus.

    Crucially, these edge cells never have a full grid of neighbours.
    """

    def setUp(self):
        """Test creating a non-grid canvas."""
        super().setUp()
        self.canvas = VisualCanvas.objects.create(
            title='Test Dynamic Canvas',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(seconds=20),
            grid_length=0,
            creator=self.super_user,
            is_torus=False
        )

    def test_unique_cell_per_canvas(self):
        """Test that duplicate cells cannot be added to a canvas."""
        self.assertEqual(self.canvas.visual_cells.count(), 0)

    def test_sequence_of_adding_cells(self):
        """Test the shape emerges contiguously by default."""
        CORRECT_CELL_ARTISTS = {
            (0, 0): 'test0',
            (0, -1): 'test1',
            (1, -1): 'test2',
            (-1, 0): 'test3',
            (1, 0): 'test4',
        }
        CORRECT_CELL_NEIGHBOURS = {
            (0, 0): {'north': None, 'north_east': None,
                     'east': (1, 0), 'south_east': (1, -1),
                     'south': (0, -1), 'south_west': None,
                     'west': (-1, 0), 'north_west': None},
            (0, -1): {'north': (0, 0), 'north_east': (1, 0),
                      'east': (1, -1), 'south_east': None,
                      'south': None, 'south_west': None,
                      'west': None, 'north_west': (-1, 0)},
            (1, -1): {'north': (1, 0), 'north_east': None,
                      'east': None, 'south_east': None,
                      'south': None, 'south_west': None,
                      'west': (0, -1), 'north_west': (0, 0)},
            (-1, 0): {'north': None, 'north_east': None,
                      'east': (0, 0), 'south_east': (0, -1),
                      'south': None, 'south_west': None,
                      'west': None, 'north_west': None},
            (1, 0): {'north': None, 'north_east': None,
                     'east': None, 'south_east': None,
                     'south': (1, -1), 'south_west': (0, -1),
                     'west': (0, 0), 'north_west': None},
        }
        users = [
            User.objects.create(username=f'test{i}', email=f'test{1}@test.com',
                                password=f'test{i}')
            for i in range(5)
        ]
        for user in users:
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
        for cell in self.canvas.visual_cells.order_by('x_position', 'y_position'):
            with self.subTest(cell=cell):
                self.assertEqual(cell.get_neighbours(as_tuple=True),
                                 CORRECT_CELL_NEIGHBOURS[cell.coordinates])
