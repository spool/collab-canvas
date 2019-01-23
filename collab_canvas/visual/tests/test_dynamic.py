from unittest import skip

from django.core.exceptions import ValidationError

from ..models import VisualCell

from .utils import BaseVisualTest, CanvasFactory, UserFactory, CellFactory


class BaseDynamicCanvasTest(BaseVisualTest):

    """Simple base class for all DynamicCanvas tests."""

    def setUp(self):
        """Test creating a non-grid canvas."""
        super().setUp()
        self.canvas = CanvasFactory(
            title='Test Dynamic Canvas',
            grid_height=0,
            grid_width=0,
            new_cells_allowed=True)


class TestGeneratingEmptyCanvas(BaseDynamicCanvasTest):

    """
    Test generating a grid that isn't a torus.

    Crucially, these edge cells never have a full grid of neighbours.
    """

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
        users = [UserFactory() for i in range(5)]
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
                self.assertEqual(
                    cell.get_neighbours(as_tuple=True,
                                        include_null_neighbours=True),
                    CORRECT_CELL_NEIGHBOURS[cell.coordinates])

    def test_no_further_available_cells(self):
        """Verify new_cells_allowed can be applied to dynamic canvases."""
        artist1 = UserFactory()
        artist2 = UserFactory()
        artist3 = UserFactory()
        self.canvas.assign_cell(artist1)
        self.canvas.assign_cell(artist2)
        self.canvas.new_cells_allowed = False
        with self.assertRaises(VisualCell.DoesNotExist) as error:
            self.canvas.assign_cell(artist3)
        self.assertIn(f"No available cells in {self.canvas} found",
                      str(error.exception))


class TestCellEditing(BaseVisualTest):

    def setUp(self):
        """Create base initialised grid for testing."""
        super().setUp()
        self.cell = CellFactory()

    def test_correct_cell_dimension(self):
        """Test cells and edits adhere to canvas cell dimensions."""
        cell_edit = self.cell.edits.create(edges_horizontal=[1] + [0]*11,
                                           edges_vertical=[0]*12,
                                           edges_south_east=[0]*9,
                                           edges_south_west=[0]*9,
                                           artist=self.cell.artist)
        cell_edit.full_clean()
        self.assertEqual(self.cell.latest_valid_edit, cell_edit)

    def test_incorrect_cell_dimensions(self):
        """Test ValidationError gets raised if dimensions are not correct."""
        cell_edit = self.cell.edits.create(edges_horizontal=[0, 1]*6,
                                           edges_vertical=[0]*12,
                                           edges_south_east=[0]*9,
                                           edges_south_west=[0]*8,
                                           artist=self.cell.artist)
        with self.assertRaises(ValidationError) as error:
            cell_edit.full_clean()
        self.assertIn(f"edges_south_west with length 8 != 9 for cell "
                      f"{self.cell}",
                      str(error.exception))

    def test_edges_delta(self):
        """Test VisualCellEdit deltas are correct."""
        cell_edit_deltas = [{
                'edges_horizontal': [0]*12,
                'edges_vertical': [0]*12,
                'edges_south_east': [0]*9,
                'edges_south_west': [0]*9,
            }, {
                'edges_horizontal': [1] + [0]*10 + [1],
                'edges_vertical': [1] + [0]*10 + [1],
                'edges_south_east': [0]*9,
                'edges_south_west': [0]*9,
            }, {
                'edges_horizontal': [-1] + [0]*10 + [-1],
                'edges_vertical': [-1, 1] + [0]*9 + [-1],
                'edges_south_east': [0]*9,
                'edges_south_west': [0]*9,
            }, {
                'edges_horizontal': [-1] + [0]*10 + [-1],
                'edges_vertical': [-1, 1] + [0]*9 + [-1],
                'edges_south_east': [0]*9,
                'edges_south_west': [0]*9,
            },
        ]
        self.cell.edits.create(edges_horizontal=[1] + [0]*10 + [1],
                               edges_vertical=[1] + [0]*10 + [1],
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9,
                               artist=self.cell.artist)
        self.cell.edits.create(edges_horizontal=[0]*12,
                               edges_vertical=[0, 1] + [0]*10,
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9,
                               artist=self.cell.artist,
                               is_valid=False)
        self.cell.edits.create(edges_horizontal=[0]*12,
                               edges_vertical=[0, 1] + [0]*10,
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9,
                               artist=self.cell.artist,)
        for i, edit in enumerate(self.cell.edits.all()):
            with self.subTest(f"Delta change {i}", i=i, edit=edit):
                self.assertEqual(edit.get_edges_delta(), cell_edit_deltas[i])

    def test_neighbour_edit(self):
        """Check edits that overlap neighbours apply with correct author."""
        CORRECT_EDGE_CELL_EDIT = {'edges_horizontal': [0, 0, 1] + [0]*9,
                                  'edges_vertical': [0]*12,
                                  'edges_south_east': [0]*9,
                                  'edges_south_west': [0]*9, }
        self.cell.canvas.new_cells_allowed = True
        self.cell.canvas.save()
        artist_1 = UserFactory()

        neighbour_cell = self.cell.canvas.assign_cell(artist_1)

        # A neighbour_cell should be contiguous with self.cell, so edge edits
        # that overlap effect both
        self.cell.edits.create(edges_horizontal=[0]*11 + [1],
                               edges_vertical=[0]*11 + [1],
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9,
                               artist=self.cell.artist)
        self.assertEqual(neighbour_cell.edits.count(), 2)
        self.assertEqual(neighbour_cell.artist, artist_1)
        self.assertIsNone(neighbour_cell.edits.first().artist)
        # self.assertEqual(neighbour_cell.edits.first().artist, artist_1)
        self.assertEqual(neighbour_cell.latest_valid_edit.artist,
                         self.cell.artist)
        for edge, edge_value in (
                neighbour_cell.latest_valid_edit.get_edges().items()
        ):
            with self.subTest(f"Assert {edge} correctly updated.",
                              edge=edge, edge_value=edge_value):
                self.assertEqual(edge_value, CORRECT_EDGE_CELL_EDIT[edge])

    @skip
    def test_circumstances_of_artists_passed(self):
        """Test artist passed for filtering vs allocating."""
        pass

    @skip
    def test_invalid_edit_skipping(self):
        """Check invalid edits show up in history and not latest_list."""
        pass

    # def test_creating_grid_permission(self):
    #     try:
    #         canvas = VisualCanvas.objects.create(
    #             title='Test Canvas',
    #             start_time=datetime.now(),
    #             end_time=datetime.now() + timedelta(seconds=20),
    #             grid_height=2,
    #             creator=self.user,
    #             is_torus=True
    #         )
    #     except VisualCanvas.PermissionError:
    #         self.assertEqual(canvas.visual_cells.count(), 7)
    #     assert False
