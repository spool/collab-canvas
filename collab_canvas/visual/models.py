"""
Models for running VisualCanvases, either initially a torus grid or organically
growing.

Todo:
    * See if the reciprocity of North<->South, East<->West is helpful.
    * Add permissions at meta level of models
    * Design a way of keeping track of edits in case reassignment is needed
    * Possibility of generating random cells
    * Rearrange default blank and random cells as cell methods
"""
from random import shuffle, choice
from typing import Dict, Tuple, Type
from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db.models import (CASCADE, SET_NULL, BigAutoField, CharField,
                              BooleanField, DateTimeField, ForeignKey, Max,
                              Model, PositiveSmallIntegerField, IntegerField,
                              SlugField, TextField, UUIDField)
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from config.settings.base import AUTH_USER_MODEL


DEFAULT_SQUARE_GRID_SIZE = 8
DEFAULT_SQUARE_CELL_SIZE = 8
DEFAULT_SQUARE_CELL_DIAGONAL_SIZE = DEFAULT_SQUARE_CELL_SIZE*2


DEFAULT_GRID_PARANTHETICAL = (
    "defaults to an "
    f"{DEFAULT_SQUARE_GRID_SIZE}x{DEFAULT_SQUARE_GRID_SIZE} grid"
)


DEFAULT_CELL_PARANTHETICAL = (
    "defaults to an "
    f"{DEFAULT_SQUARE_CELL_SIZE}x{DEFAULT_SQUARE_CELL_SIZE} cell"
)


class VisualCanvas(Model):

    """
    Canvas for visual collaboration.

    Each canvas has a start and end date, and normal users may only edit one
    cell. If a torus then the grid height and width must be defined. If not a
    torus then grid_width and grid_height will enforce the maximum edges but
    not connect edge neighbours. If grid height and width are 0 and
    new_cells_allowed is True then the canvas will grow with positive and
    negative coordinates organically with each new artist.

    Todo:
        * Consider more flexible canvas shapes
        * Consider at least allowing x/y width and height
        * Possibility of resizing canvas and making dynamic in future
        * Way of enforing cell_divisions to cells and edits
    """
    id = UUIDField(default=uuid4, primary_key=True, editable=False)
    title = CharField(_("Canvas Title"), max_length=100)
    slug = SlugField(_("URL Compliant Title"), unique=True)
    description = TextField(max_length=200, blank=True)
    created_at = DateTimeField(_("Date Created"), auto_now_add=True)
    start_time = DateTimeField(_("Start Time of Public Canvas Editing"))
    end_time = DateTimeField(_("Time the Canvas Will Stop Accepting Edits"))
    grid_width = PositiveSmallIntegerField(
        _("Grid horizontal (x) length, where max number of cells is this "
          f"times grid_height ({DEFAULT_GRID_PARANTHETICAL})"),
        default=DEFAULT_SQUARE_GRID_SIZE,)  # Default assumes a square grid
    grid_height = PositiveSmallIntegerField(
        _("Grid vertical (y) length, where max number of cells is this "
          f"times grid_width ({DEFAULT_GRID_PARANTHETICAL})"),
        default=DEFAULT_SQUARE_GRID_SIZE,)  # Default assumes a square grid
    # cell_divisions = PositiveSmallIntegerField(_("Cell Divisions"), default=8)
    # There's a possibilty for a 3rd dimension in future if helpful
    cell_width = PositiveSmallIntegerField(_("Width of cell grid "
                                             f"({DEFAULT_CELL_PARANTHETICAL})"),
                                           default=DEFAULT_SQUARE_CELL_SIZE)
    cell_height = PositiveSmallIntegerField(_("Height of cell grid "
                                              f"({DEFAULT_CELL_PARANTHETICAL})"),
                                            default=DEFAULT_SQUARE_CELL_SIZE)
    # cell_type = PositiveSmallIntegerField("Diagonal")
    cell_colour_range = PositiveSmallIntegerField(
        _("Maximum range of colours"), default=1)
    creator = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE,
                         verbose_name=_("Person who created this Visual "
                                        "Canvas"))
    is_torus = BooleanField(_("Initialize a torus grid that can't be changed"),
                            default=False)
    new_cells_allowed = BooleanField(_("Allow new cells to be added"),
                                     default=False)

    def __str__(self):
        return f'{self.title} ends {self.end_time:%Y-%m-%d %H:%M}'

    class Meta:
        verbose_name_plural = "visual canvases"

    @property
    def is_grid(self):
        """Test if both grid_width and grid_height are > 0."""
        return 0 < self.grid_width and 0 < self.grid_height

    def clean(self):
        if self.is_torus and self.new_cells_allowed:
            raise ValidationError(_('Torus VisualCanvases cannot add '
                                    'new cells.'))
        if self.is_torus and not self.is_grid:
            raise ValidationError(_(f'Torus {self} must  have a width and '
                                    'height'))

    def generate_grid(self, can_add=False):
        """Generate a grid."""
        cell_count = self.visual_cells.count()
        if self.is_grid and cell_count == 0:
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    self.visual_cells.create(x_position=x, y_position=y,
                                             width=self.cell_width,
                                             height=self.cell_height,
                                             colour_range=self.cell_colour_range)
        elif self.is_grid and can_add and not self.is_torus:
            try:
                current_max_x, current_max_y = self.visual_cells.aggregate(
                    Max('x_position'), Max('y_position')).values()
                assert (current_max_x < self.max_coordinates[0] or
                        current_max_y < self.max_coordinates[1])
            except AssertionError:
                raise ValidationError(_("Cannot add to grid unless both "
                                        "previous grid max_coordinates "
                                        f"({current_max_x}, {current_max_y}) "
                                        "are < set max_coordinates "
                                        f"{self.max_coordinates} for canvas "
                                        f"{self.title}"))
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    if x > current_max_x or y > current_max_y:
                        self.visual_cells.create(x_position=x, y_position=y,
                                                 width=self.cell_width,
                                                 height=self.cell_height,
                                                 colour_range=self.cell_colour_range)
        elif not can_add and not self.is_torus:
            raise ValidationError(_("Cells can only be added to a grid if "
                                    "can_add=True"))
        elif self.is_torus and cell_count > 0:
            raise ValidationError(_("Cells cannot be added to a torus that "
                                    f"already has {cell_count} cells"))

    @property
    def max_coordinates(self):
        """
        Maximum point for a grid.

        Note:
            * Implemented in case of future non-square (use grid_width if so).
        """
        if not self.is_grid:
            raise ValidationError(_('Max of coordinates requires a defined '
                                    'grid'))
        return (self.grid_width - 1, self.grid_height - 1)

    def get_centre_cell_coordinates(self):
        """
        Apprixmate the centre most cell.

        If the canvas is a grid, the floor middle x and y, otherwise (0, 0).

        Todo:
            * Consider ways of approximating the centre of other shapes
        """
        if self.is_grid:
            return (self.max_coordinates[0]//2, self.max_coordinates[1]//2)
        else:
            return (0, 0)

    def get_random_cell_coordinates(self):
        """
        Get pure random cell (possibly just coordinates of) from canvas.

        Todo:
            * Add errors for cases of non-grid
            * Consdier removing random for dynamic grid
        """
        if self.is_grid:  # Note: must add 1 to include max coordinates
            return (choice(list(range(self.max_coordinates[0] + 1))),
                    choice(list(range(self.max_coordinates[1] + 1))))
        else:
            self.visual_cells.order_by('?').first().coordinates

    def correct_coordinates_for_torus(self, coordinates):
        """
        Enforce coordinates for a torus grid.

        This method projects negative coordinates to positive ones. Requires
        a torus of height >= 3.

        Todo:
            * Rewrite to more efficiently handle type issues.
            * Try to just handle tuples better
        """
        type_correct = False
        if type(coordinates) is not list:
            coordinates = list(coordinates)
            type_correct = True
        if coordinates[0] > self.max_coordinates[0]:
            coordinates[0] = 0
        elif coordinates[0] < 0:
            coordinates[0] = self.max_coordinates[0]
        if coordinates[1] > self.max_coordinates[1]:
            coordinates[1] = 0
        elif coordinates[1] < 0:
            coordinates[1] = self.max_coordinates[1]
        if type_correct:
            return tuple(coordinates)
        return coordinates

    # def find_empty_torus_cell(self):
    #     """Query for place for a new cell."""
    #     coordinate_differences = ADJACENT_COORDINATES.values()
    #     available_cells = self.visual_cells.filter(artist__isnull=True)
    #                                                   # Q(north__isnull=True) |
    #                                                   # Q(east__isnull=True) |
    #                                                   # Q(south__isnull=True) |
    #                                                   # Q(west__isnull=True))
    #     if not available_cells.exists():
    #         raise ValidationError(_('No more cells available.'))
    #     cells = self.visual_cells.values_list('x_position', 'y_position')
    #     shuffle(cells)
    #     for cell in cells:
    #         if
    #     return choice(available_cells)

    INITIAL_CELL_METHODS = {
        'centre': 'get_centre_cell_coordinates',
        'random': 'get_random_cell_coordinates',
    }

    def choose_initial_cell(self, first_cell_algorithm: str = 'centre',
                            width: int = None, height: int = None,
                            colour_range: int = None, **kwargs):
        """Select first cell based on canvas_type and first_cell_algorithm."""
        width = width or self.cell_width
        height = height or self.cell_height
        colour_range = colour_range or self.cell_colour_range
        if self.new_cells_allowed:
            return self.visual_cells.create(x_position=0, y_position=0,
                                            width=width, height=height,
                                            colour_range=colour_range,
                                            **kwargs)
        else:
            coords = getattr(
                self, self.INITIAL_CELL_METHODS[first_cell_algorithm])()
            return self.visual_cells.get(x_position=coords[0],
                                         y_position=coords[1],
                                         width=width, height=height,
                                         colour_range=colour_range, **kwargs)

    def get_or_create_contiguous_cell(self,
                                      first_cell_algorithm: str = 'centre',
                                      width: int = None,
                                      height: int = None,
                                      colour_range: int = None,
                                      # artist: Type[AUTH_USER_MODEL] = None,
                                      **kwargs):
        """
        Find a continguous cell that's not owned

        Todo:
            * Refactor to reduce complexity
            * Test algorithm dict method
            * Consdier ways of auto-filtering to edges of allocated cells
            * Consider possibility of separate bubbles that can connect with basic radius
            * Determine a means of dealing with passing an artist
        """
        # if self.torus_grid:
        #     raise ValidationError(_('New cells cannot be added to a torus grid.'))
        # else:
        #    edge_cells =  self.visual_cells.exclude(Q(north__isnull=True) &
        #                                              Q(east__isnull=True) &
        #                                              Q(south__isnull=True) &
        #                                              Q(west__isnull=True))
        # if self.torus_grid:
        #     x_direction = 1
        #     y_direction = 1
        # else:
        #     x_direction = choose([-1, 1])
        #     y_direction = choice([-1, 1])
        # x_limit =
        # if self.torus_grid:
        #     cells = self.visual_cells.filter(artist__isnull=True)
        # else:
        width = width or self.cell_width
        height = height or self.cell_height
        colour_range = colour_range or self.cell_colour_range
        # Retrieve all cells currently allocated to artists so future cells are
        # added contiguously to them
        allocated_cells = list(self.visual_cells.exclude(
            artist__isnull=True).values_list('x_position', 'y_position'))
        if not allocated_cells:
            return self.choose_initial_cell(first_cell_algorithm)
        if (self.is_grid and
                len(allocated_cells) >= self.grid_height*self.grid_width):
            raise self.FullGridException
        COORDINATE_DIFFERENCES = list(VisualCell.ADJACENT_COORDINATES.values())
        shuffle(allocated_cells)
        for cell in allocated_cells:
            shuffle(COORDINATE_DIFFERENCES)
            for coordinate_difference in COORDINATE_DIFFERENCES:
                potential_cell = (cell[0] + coordinate_difference[0],
                                  cell[1] + coordinate_difference[1])
                if potential_cell not in allocated_cells:  # Might choose a pre-allocated cell
                    if self.new_cells_allowed:
                        return VisualCell(canvas=self,
                                          x_position=potential_cell[0],
                                          y_position=potential_cell[1],
                                          width=width, height=height,
                                          colour_range=colour_range,
                                          **kwargs)
                    if self.is_torus:
                        potential_cell = self.correct_coordinates_for_torus(
                            potential_cell)
                        if potential_cell in allocated_cells:
                            continue
                    else:  # Grid but not torus
                        if (not 0 <= potential_cell[0] < self.grid_width or
                                not 0 <= potential_cell[1] < self.grid_height):
                            continue
                    try:
                        blank_cell = self.visual_cells.get(
                            x_position=potential_cell[0],
                            y_position=potential_cell[1], width=width,
                            height=height, colour_range=colour_range, **kwargs)
                        if not blank_cell.artist:
                            return blank_cell
                    except VisualCell.DoesNotExist:
                        raise VisualCell.DoesNotExist(_("No cell with that position"))
                    except AssertionError:
                        raise ValidationError(_("That cell is already owned by "
                                                f"another artist {blank_cell.artist}"))
        raise VisualCell.DoesNotExist(_(f"No available cells in {self} found"))

    def get_or_assign_cell(self, artist: Type[AUTH_USER_MODEL], *args,
                           **kwargs):
        """Either create or assign a cell for passed artist if possible."""
        try:
            cell = self.visual_cells.get(artist=artist, *args, **kwargs)
            return cell
        except VisualCell.DoesNotExist:
            cell = self.get_or_create_contiguous_cell(*args, **kwargs)
            cell.artist = artist
            cell.full_clean()
            cell.save()
            return cell

    # def artists(self):
    #     """Return a querset of all currently assigned artists."""
    #     self.cells

    class FullGridException(Exception):
        pass

    def save(self, *args, **kwargs):
        """
        Save VisualCanvas, enforcing slug creation and torus if selected.

        Todo:
            * Consider if it's worth initiating a first cell when not a torus.
        """
        if not self.id:
            self.slug = slugify(self.title)
            # if self.grid_height:
            #     self.generate_grid()
            #     # self.initiate_torus_links()
        if bool(self.grid_width) ^ bool(self.grid_height):  # NOR len or width
            if not bool(self.grid_width):  # Not grid_height should then be set
                self.grid_width = 1
            else:
                self.grid_height = 1       # Not grid_width implied by `if`
        if self.is_torus:
            try:
                assert 2 < self.grid_width and 2 < self.grid_height
            except AssertionError:
                raise ValidationError(_(f'Width {self.grid_width} < 3 and/or '
                                        f'length {self.grid_height} < 3'))
        try:
            assert self.start_time < self.end_time
        except AssertionError:
            raise ValidationError(_(f'start_time {self.start_time} must be earlier '
                                    f'than end_time {self.end_time}'))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        return reverse("users:detail", kwargs={"username": self.username})

        Sort UUIDs for canvases. Cell coordinates are urls.
        """
        return reverse('visual:canvas', kwargs={'canvas_id': self.id})


# class TorusEdgeCellsManager(Manager):
#
#     """Extract the set of cells in a torus that don't have all adjacents owned."""
#
#     def get_queryset(self):
#         return super().get_queryset().filter(artist__isnull=True,
#                                              Q(north__isnull=True) |
#                                              Q(east__isnull=True) |
#                                              Q(south__isnull=True) |
#                                              Q(west__isnull=True))
#
#
# class EdgeCellsManager(Manager):
#
#     """Extract the set of cells that don't have all adjacents occupied."""
#
#     def get_queryset(self):
#         return super().get_queryset().filter(Q(north__isnull=True) |
#                                              Q(east__isnull=True) |
#                                              Q(south__isnull=True) |
#                                              Q(west__isnull=True))


class VisualCell(Model):

    """
    A cell in a VisualCanvas.

    Todo:
        * Consider an automatic null initial cell
        * Consider enforcing Cell Dimensions (and potential flexibility).
        * Random cell generator (remove from Grid contructor)
        * Consider adding description, or json or both
        * Combine ADJACENT_NEIGHBOUR_CHOICES and ADJACENT_COORDINATES
        * Consider adding https://mypy.readthedocs.io/en/latest/final_attrs.html
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    ADJACENT_CHOICES = (
        (NORTH, 'north'),
        (EAST, 'east'),
        (SOUTH, 'south'),
        (WEST, 'west'),
    )

    ADJACENT_COORDINATES = {
        'north': (0, 1),
        'east': (1, 0),
        'south': (0, -1),
        'west': (-1, 0),
    }

    CORNER_COORDINATES = {
        'north_east': (1, 1),
        'south_east': (1, -1),
        'south_west': (-1, -1),
        'north_west': (-1, 1),
    }

    NEIGHBOUR_COORDINATES = {
        **ADJACENT_COORDINATES,
        **CORNER_COORDINATES
    }

    # Assuming as cells have the same dimensions (default cells)
    # ADJACENT_NEIGHBOUR_EDGES = {
    #     'north': self.lattice_dimensions['edges_horizontal'][-self.width:],
    #     'east': self.lattice_dimensions['edges_vertical'][self.height:],
    #     'south': self.lattice_dimensions['edges_horizontal'][self.width:],
    #     'west': self.lattice_dimensions['edges_vertical'][-self.height:],
    # }

    id = UUIDField(default=uuid4, primary_key=True, editable=False)
    canvas = ForeignKey(VisualCanvas, on_delete=CASCADE,
                        related_name='visual_cells',
                        verbose_name=_("Which canvas this cell is in"))
    artist = ForeignKey(AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=SET_NULL, related_name='visual_cells',
                        verbose_name=_("Artist assigned this part of the Canvas"),)
    created_at = DateTimeField(_("Date cell was created"), auto_now_add=True)
    x_position = IntegerField(_("Horizontal position relative to 0"))
    y_position = IntegerField(_("Veritical position relative to 0"))
    width = PositiveSmallIntegerField(_("Width of cell grid "
                                        f"(DEFAULT_CELL_PARANTHETICAL)"),
                                      default=DEFAULT_SQUARE_CELL_SIZE,
                                      db_column='x_len')
    height = PositiveSmallIntegerField(_("Height of cell grid "
                                         f"(DEFAULT_CELL_PARANTHETICAL)"),
                                       default=DEFAULT_SQUARE_CELL_SIZE,
                                       db_column='y_len')
    south_east_diagonals = PositiveSmallIntegerField(
        "Length of south east pointed diagonal segments "
        f"(DEFAULT_CELL_PARANTHETICAL)",
        default=DEFAULT_SQUARE_CELL_DIAGONAL_SIZE,
        db_column='z_len')
    south_west_diagonals = PositiveSmallIntegerField(
        "Length of south east pointed diagonal segments "
        f"(DEFAULT_CELL_PARANTHETICAL)",
        default=DEFAULT_SQUARE_CELL_DIAGONAL_SIZE,
        db_column='t_len')
    colour_range = PositiveSmallIntegerField(_("Maximum range of colours"),
                                             default=1)
    is_editable = BooleanField(_("Whether artists are allowed to edit this "
                                 "cell"), default=True)
    neighbours_may_edit = BooleanField(_("Whether artist's neighbours are allowed "
                                         "to edit this cell"), default=True)

    class Meta:

        """Enforce efficiency and correctness within each canvas."""

        unique_together = (("canvas", "artist"),
                           ("canvas", "x_position", "y_position"))

    def clean(self):
        """Means of testing if cell is outside a pre-defined grid."""
        if ((self.canvas.grid_height or self.canvas.grid_width) and
                (not self.canvas.grid_width > self.x_position >= 0 or
                 not self.canvas.grid_height > self.y_position >= 0)):
            raise ValidationError(_(f'Cell position {self.coordinates} is '
                                    'outside the grid'))

    # def save(self):
    #     """Initiate a first edit upon creation, including neighboring edges."""
    #     if self.neighbours_may_edit:
    #         if not self.id:
    #             self.initialise_with_neighbour_edges()
    #         elif

    @property
    def adjacent_neighbour_portions(self):
        return {'north': {'edge_name': 'edges_horizontal',
                          'self_portion': self.width,
                          'neighbour_portion': -self.width},
                'east': {'edge_name': 'edges_vertical',
                         'self_portion': -self.height,
                         'neighbour_portion': self.height},
                'south': {'edge_name': 'edges_horizontal',
                          'self_portion': -self.width,
                          'neighbour_portion': self.width},
                'west': {'edge_name': 'edges_horizontal',
                         'self_portion': self.height,
                         'neighbour_portion': -self.height}, }

    def default_blank_cell(self):
        return {k: [0]*l for k, l in self.lattice_dimensions.items()}

    def set_blank(self, **kwargs):
        self.edits.create(**self.default_blank_cell(), **kwargs)

    # @staticmethod
    # def set_neighbour_edge(edges, edge: str, self_portion: int,
    #                        neighbour_portion: int) -> dict:
    # # Set the cell section based on the range in each
    # # adjacent_neighbour_portions configuration
    # if portion[self_portion] > 0:
    #     if portion[neighbour_portion] > 0:
    #         edges[portion[edge]][:portion[self_portion]] = (
    #             getattr(neighbour.latest_valid_edit,
    #                     portion[edge])[:neighbour_portion]
    #         )
    #     else:  # neighbour_portion < 0, so apply to
    #         edges[portion[edge]][:portion[self_portion]] = (
    #             getattr(neighbour.latest_valid_edit,
    #                     portion[edge])[neighbour_portion:]
    #         )
    # else:  # self_portion < 0, so copy to end of the affected edge
    #     if portion[neighbour_portion] > 0:
    #         edges[portion[edge]][portion[self_portion]:] = (
    #             getattr(neighbour.latest_valid_edit,
    #                     portion[edge])[:neighbour_portion]
    #         )
    #     else:
    #         edges[portion[edge]][portion[self_portion]:] = (
    #             getattr(neighbour.latest_valid_edit,
    #                     portion[edge])[neighbour_portion:]
    #         )

    def get_blank_with_neighbour_edges(self, **kwargs):
        """Get the neighbours' current edge states."""
        edges_dict = self.default_blank_cell()
        neighbours = self.get_neighbours(
            neighbour_coords=self.ADJACENT_COORDINATES)
        for direction, neighbour in neighbours.items():
            if neighbour:
                edge_name, self_portion, neighbour_portion = (
                    self.adjacent_neighbour_portions[direction].values()
                )  # This assumes python >=3.7 where dicts are ordered
                edge_segment = edges_dict[edge_name]
                neighbour_segment = getattr(neighbour.latest_valid_edit, edge_name)
                neighbour_edge = (neighbour_segment[:neighbour_portion] if
                                  neighbour_portion > 0
                                  else neighbour_segment[neighbour_portion:])
                if self_portion > 0:
                    # Todo: check these are the right portions
                    edge_segment[:self_portion] = neighbour_edge
                else:
                    edge_segment[self_portion:] = neighbour_edge
        return edges_dict

    def extract_neighbour_edge_deltas(self):
        """
        Extract deltas that may need to be applied to neighbours.

        Note:
            * Currently only gets from latest *valid* edit
        """
        neighbours = {}
        delta = self.latest_valid_edit.get_edges_delta()
        for direction, edge_segment in (
                self.adjacent_neighbour_portions.items()
        ):
            edge = delta[edge_segment['edge_name']]
            segment = edge_segment['self_portion']
            delta_portion = edge[:segment] if segment > 0 else edge[segment:]
            if 1 in delta_portion or -1 in delta_portion:
                neighbours[direction] = {
                    'edge_name': edge_segment['edge_name'],
                    'edge': edge,
                    'edge_delta': delta_portion,
                    'segment': edge_segment['neighbour_portion']}
        return neighbours

    def dispatch_neighbour_edits(self):
        delta_portions = self.extract_neighbour_edge_deltas()
        if delta_portions:
            neighbour_coordinates_dict = {k: self.ADJACENT_COORDINATES[k]
                                          for k in delta_portions}
            neighbours = self.get_neighbours(
                neighbour_coords=neighbour_coordinates_dict)
            for direction, neighbour in neighbours.items():
                edge_name, edge, edge_delta, segment = (
                    delta_portions[direction].values()
                )
                neighbour_latest = neighbour.latest_valid_edit
                neighbour_latest.id = None  # Copies the most recent instance
                neighbour_latest.artist = self.artist
                latest_edge = getattr(neighbour_latest, edge_name)
                # Todo: check these are the right portions
                new_edge = (edge_delta + latest_edge[segment:] if segment > 0
                            else latest_edge[:segment] + edge_delta)
                setattr(neighbour_latest, edge_name, new_edge)
                neighbour_latest.full_clean()
                neighbour_latest.save()

    @property
    def lattice_dimensions(self):
        """Default ratios of lengths of rectangular cells with diagonals."""
        return {'edges_horizontal': self.width**2 + self.width,
                'edges_vertical': self.height**2 + self.height,
                'edges_south_east': self.width*self.height,
                'edges_south_west': self.width*self.height, }

    @property
    def coordinates(self):
        return (self.x_position, self.y_position)

    # north = ForeignKey('VisualCell', related_name="south_cell", blank=True,
    #                    null=True, on_delete=SET_NULL)
    # north_east = ForeignKey('VisualCell', related_name="south_west_cell",
    #                        blank=True, null=True, on_delete=SET_NULL)
    # east = ForeignKey('VisualCell', related_name="west_cell", blank=True,
    #                   null=True, on_delete=SET_NULL)
    # south_east = ForeignKey('VisualCell', related_name="north_west_cell",
    #                        blank=True, null=True, on_delete=SET_NULL)
    # south = ForeignKey('VisualCell', related_name="north_cell", blank=True,
    #                    null=True, on_delete=SET_NULL)
    # south_west = ForeignKey('VisualCell', related_name="north_east_cell",
    #                        blank=True, null=True, on_delete=SET_NULL)
    # west = ForeignKey('VisualCell', related_name="east_cell", blank=True,
    #                   null=True, on_delete=SET_NULL)
    # north_west = ForeignKey('VisualCell', related_name="south_east_cell",
    #                        blank=True, null=True, on_delete=SET_NULL)

    # class Meta:
    #     unique_together = (('canvas', 'x_position', 'y_position'),
    #                        ('canvas', 'artist'))
    #                        ('canvas', 'artist'))
    #                        ('north', 'east', 'south', 'west'))

    # objects = Manager()
    # edge_cells = EdgeCellsManager()
    # torus_edge_cells = TorusEdgeCellsManager()

    def get_absolute_url(self):
        """Canvas url and uuid to retain anonymity in cell position."""
        return reverse('visual:cell', kwargs={'cell_id': self.id})

    def get_edit_url(self):
        """Return edit url."""
        return reverse('visual:cell-edit', kwargs={'cell_id': self.id})

    def __str__(self):
        return (
            f'({self.x_position}, {self.y_position}) '
            f'{self.canvas} - '
            f'{self.artist.username if self.artist else "Not assigned"}'
        )

    def get_neighbours(self, as_tuple: bool = False,
                       neighbour_coords: Dict[str, Tuple[int, int]] = None,
                       include_null_neighbours: bool = False):
        """
        Return Moore's neighbours, including torus neighbours if appropriate.
        """
        neighbour_coords = neighbour_coords or self.NEIGHBOUR_COORDINATES
        neighbours = {}
        for direction, coordinate_difference in neighbour_coords.items():
            coords = (self.x_position + coordinate_difference[0],
                      self.y_position + coordinate_difference[1])
            if self.canvas.is_torus:
                coords = self.canvas.correct_coordinates_for_torus(coords)
            try:
                neighbour = self.canvas.visual_cells.get(x_position=coords[0],
                                                         y_position=coords[1])
            except VisualCell.DoesNotExist:
                neighbour = None
            if neighbour:
                if as_tuple:
                    neighbours[direction] = neighbour.coordinates
                else:
                    neighbours[direction] = neighbour
            elif include_null_neighbours:
                neighbours[direction] = neighbour
        return neighbours

    @property
    def edit_ids(self):
        """List of all edit ids (no filtering)."""
        return list(self.get_visualcelledit_order())

    @property
    def valid_edit_ids(self):
        """List of valid edits."""
        return list(self.edits.filter(is_valid=True).values_list('id',
                                                                 flat=True))

    @property
    def latest_valid_edit(self):
        """Latest valid edit, often for display to artists for further edits."""
        return self.edits.filter(is_valid=True).latest()

    # def set_neighbours(self):
    #     for direction, coordinates in CELL_NEIGHBOURS.items():
    #         try:
    #             neighbour = self.canvas.visual_cells.get(x_position=coordinates[0],
    #                                                         y_position=coordinates[1])
    #         except VisualCell.DoesNotExist:
    #             neighbour = None
    #         setattr(self, direction, neighbour)

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.edits = [self.blank_cell()]
    #     super().save(*args, **kwargs)


class VisualCellEdit(Model):

    """
    Timestamped edits to cells.

    Todo:
        * Decide if it's worth including a hidden option here and Cell (in case
        of time series reveal). Could be questions of who it's hidden for...
        * Decide if a boolean 'submit' (or similar) is worth including to
        indicate artist's sense of "completion"
        * Whether it's worth marking with comments
        * Whether a sequence number is worth saving
        * How to mark issues or skips in time series
        * See if it's worth adding ordering to Meta
        * See if the order_with_respect_to is worth it...
        * Check if adding user id is helpful in case cell gets re-assigned
    """

    EDGE_FIELD_PREFIX = 'edges_'

    id = BigAutoField(primary_key=True)
    cell = ForeignKey(VisualCell, on_delete=CASCADE, related_name="edits")
    artist = ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    edges_horizontal = ArrayField(PositiveSmallIntegerField(), db_column='x')
    edges_vertical = ArrayField(PositiveSmallIntegerField(), db_column='y')
    edges_south_east = ArrayField(PositiveSmallIntegerField(), db_column='z')
    edges_south_west = ArrayField(PositiveSmallIntegerField(), db_column='t')
    is_valid = BooleanField(_("Whether the edit is valid and included "
                              "in time series"), default=True)
    neighbour_edit = PositiveSmallIntegerField(
        _("Which neighbour, if any, is the source of the edit"),
        blank=True, null=True, choices=VisualCell.ADJACENT_CHOICES)

    def __str__(self):
        """
        Artist (if specified) and timestamp

        Todo:
            * Improve this to reflect cell assignment and artist differences.
        """
        state = f'{self.artist} ' if self.artist else 'Empty '
        return state + f'{self.timestamp}'

    def get_absolute_url(self):
        """Using Canvas and Cell uuids to be able to reconstruct ordering."""
        return reverse('visual:cell-history',
                       kwargs={'cell_id': self.cell.id,
                               'cell_history': self.history_number})

    @classmethod
    def get_edge_names(cls):
        """Currently returns all egdes, but may be restrictable in future."""
        return [field.name for field in cls._meta.get_fields()
                if field.name.startswith(cls.EDGE_FIELD_PREFIX)]

    def get_edges(self):
        """Return a dict of edges."""
        return {edge_name: getattr(self, edge_name) for edge_name in
                self.get_edge_names()}

    # def get_edges(self):
    #     """Yield edges as tuples of name and value."""
    #     for edge_name in self.get_edge_names():
    #         yield edge_name, getatrr()

    def get_edges_delta(self, valid_only: bool = True):
        """
        Get difference in edge vector between self and valid predecessor.

        Note:
            * If valid_only is False then it will be delta with respect to
            timestamp.
        """
        previous_edit = (self.get_previous_valid_edit() if valid_only else
                         self.get_previous_in_order())
        if previous_edit:
            delta = {}
            for edge_name in self.get_edge_names():
                delta[edge_name] = [current - previous for current, previous in
                                    zip(getattr(self, edge_name),
                                        getattr(previous_edit, edge_name))]
            return delta
        else:
            return self.cell.get_blank_with_neighbour_edges()

    def get_previous_valid_edit(self):
        """Get previous edit where is_valid is true."""
        try:
            edit = self.get_previous_in_order()
            # i = 0
            while True:
                if edit.is_valid:
                    return edit
                edit = edit.get_previous_in_order()
                # if i == 7:
                #     assert False
                # i += 1
        except VisualCellEdit.DoesNotExist:
            return None
        # while not edit.is_valid:
        #     edit = self.get_previous_in_order()
        # # else:
        # #     return None  # If the loop finishes before valid_edit is found
        # return edit

    @property
    def history_number(self):
        """Return number in cell's history, irrespective of is_valid."""
        return self.cell.edit_ids.index(self.id)  # index finds first match in list

    @property
    def edit_number(self):
        """Return what number edit this is of valid edits to parent cell."""
        try:
            return self.cell.valid_edit_ids.index(self.id)
        except ValueError:  # cell has no edit number if not valid
            return None

    def clean(self):
        """Ensure array dimensions adhere to cell dimensions."""
        for attr_name, length in self.cell.lattice_dimensions.items():
            # if not getattr(self, attr_name):
            #     setattr(self, attr_name,
            #             getattr(self.get_previous_in_order(), attr_name))
            # Todo: https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/fields/#len
            if len(getattr(self, attr_name)) != length:
                raise ValidationError(f"{attr_name} with length "
                                      f"{len(getattr(self, attr_name))} != "
                                      f"{length} for cell {self.cell}")

    class Meta:
        """
        Designed to enfornce retaining information about each edit.

        Note:
            * Cannot have `order_with_respect_to` and `ordering` together.
            * Enforcing permission is key
        """
        order_with_respect_to = 'cell'
        get_latest_by = 'timestamp'  # Hopefully order_with_respect_to + get
