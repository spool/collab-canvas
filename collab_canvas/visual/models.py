"""
Models for running VisualCanvases, either initially a torus grid or organically
growing.

Todo:
    * See if the reciprocity of North<->South, East<->West is helpful.
"""
from config.settings.base import AUTH_USER_MODEL

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db.models import (CASCADE, SET_NULL, CharField, BooleanField,
                              DateTimeField, ForeignKey, Max, Model,
                              PositiveSmallIntegerField, IntegerField,
                              SlugField, TextField)
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from random import shuffle, choice


CELL_ADJACENTS = {
    'north': (0, 1),
    'east': (1, 0),
    'south': (0, -1),
    'west': (-1, 0),
}

CELL_CORNERS = {
    'north_east': (1, 1),
    'south_east': (1, -1),
    'south_west': (-1, -1),
    'north_west': (-1, 1),
}


CELL_NEIGHBOURS = {
    **CELL_ADJACENTS,
    **CELL_CORNERS
}


class VisualCanvas(Model):

    """
    Canvas for visual collaboration.

    Each canvas has a start and end date, and normal users may only edit one
    cell. If a torus then the grid height and width must be defined. If not a
    torus then grid_width and grid_height will enforce the maximum edges but
    not connect edge neighbours. If grid height and width are 0 and
    new_cell_allowed is True then the canvas will grow with positive and
    negative coordinates organically with each new artist.

    Todo:
        * Consider more flexible canvas shapes
        * Consider at least allowing x/y height and width
        * Possibility of resizing canvas and making dynamic in future
    """

    title = CharField(_("Canvas Title"), max_length=100)
    slug = SlugField(_("URL Compliant Title"), unique=True)
    description = TextField(max_length=200, blank=True)
    start_time = DateTimeField(_("Start Time of Public Canvas Editing"))
    end_time = DateTimeField(_("Time the Canvas Will Stop Accepting Edits"))
    grid_width = PositiveSmallIntegerField(
        _("Grid horizontal (x) length, where max number of cells is this "
          "times grid_height."),
        default=8,)  # Default assumes a square grid
    grid_height = PositiveSmallIntegerField(
        _("Grid vertical (y) length, where max number of cells is this "
          "time grid_width."),
        default=8,)  # Default assumes a square grid
    cell_divisions = PositiveSmallIntegerField(_("Cell Divisions"), default=8)
    creator = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE,
                         verbose_name=_("Person who created this Visual "
                                        "Canvas"))
    is_torus = BooleanField(_("Initialize a torus grid that can't be changed"),
                            default=False)
    new_cells_allowed = BooleanField(_("Allow new cells to be added"),
                                     default=False)

    def __str__(self):
        return f'{self.title} ends {self.end_time:%Y-%m-%d %H:%M}'

    @property
    def is_grid(self):
        """Test if both grid_width and grid_height are > 0."""
        return self.grid_width > 0 and self.grid_height > 0

    def clean(self):
        if self.is_torus and self.new_cells_allowed:
            raise ValidationError(_('Torus VisualCanvases cannot add '
                                    'new cells.'))
        if self.is_torus and not self.is_grid:
            raise ValidationError(_('Torus VisualCanvases must have a height'))

    def generate_grid(self, add=False):
        """Generate a torus grid."""
        if self.is_grid and self.visual_cells.count() == 0:
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    self.visual_cells.create(x_position=x, y_position=y)
        elif self.is_grid and add:
            try:
                current_max_x, current_max_y = self.visual_cells.aggregate(
                    Max('x_position'), Max('y_position')).values()
                assert (current_max_x < self.max_coordinates[0] or
                        current_max_y < self.max_coordinates[1])
            except AssertionError:
                raise ValidationError(_("Cannot add to grid unless both "
                                        f"previous grid max_coordinates "
                                        f"({current_max_x}, {current_max_y}) "
                                        "are < set max_coordinates "
                                        f"{self.max_coordinates} for canvas "
                                        f"{self.title}"))
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    if x > current_max_x or y > current_max_y:
                        self.visual_cells.create(x_position=x, y_position=y)
        elif not add:
            raise ValidationError(_("Cells can only be added to a grid if "
                                    "add=True"))

    @property
    def max_coordinates(self):
        """
        Maximum point for torus grid.

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
    #     coordinate_differences = CELL_ADJACENTS.values()
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

    def choose_initial_cell(self, first_cell_algorithm='centre'):
        """Select first cell based on canvas_type and first_cell_algorithm."""
        if self.new_cells_allowed:
            return self.visual_cells.create(x_position=0, y_position=0)
        else:
            coords = getattr(
                self, self.INITIAL_CELL_METHODS[first_cell_algorithm])()
            return self.visual_cells.get(x_position=coords[0],
                                         y_position=coords[1])

    def get_or_create_contiguous_cell(self, first_cell_algorithm='centre'):
        """
        Find a continguous cell that's not owned

        Todo:
            * Test algorithm dict method
            * Consdier ways of auto-filtering to edges of allocated cells
            * Consider possibility of separate bubbles that can connect with basic radius
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
        allocated_cells = list(self.visual_cells.exclude(
            artist__isnull=True).values_list('x_position', 'y_position'))
        if not allocated_cells:
            return self.choose_initial_cell(first_cell_algorithm)
        if (self.is_grid and
                len(allocated_cells) >= self.grid_height*self.grid_width):
            raise self.FullGridException
        COORDINATE_DIFFERENCES = list(CELL_ADJACENTS.values())
        shuffle(allocated_cells)
        for cell in allocated_cells:
            shuffle(COORDINATE_DIFFERENCES)
            for coordinate_difference in COORDINATE_DIFFERENCES:
                potential_cell = (cell[0] + coordinate_difference[0],
                                  cell[1] + coordinate_difference[1])
                if potential_cell not in allocated_cells:  # Might choose a pre-allocated cell
                    if self.new_cells_allowed:
                        return VisualCell(x_position=potential_cell[0],
                                          y_position=potential_cell[1],
                                          canvas=self)
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
                            y_position=potential_cell[1])
                        assert blank_cell.artist is None
                        return blank_cell
                    except VisualCell.DoesNotExist:
                        raise VisualCell.DoesNotExist(_("No cell with that position"))
                    except AssertionError:
                        raise ValidationError(_("That cell is already owned by "
                                                f"another artist {blank_cell.artist}"))

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
        super().save(*args, **kwargs)


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

    """A cell in a VisualCanvas."""

    canvas = ForeignKey(VisualCanvas, on_delete=CASCADE,
                        related_name='visual_cells',
                        verbose_name=_("Canvas Cell is Associated With"))
    artist = ForeignKey(AUTH_USER_MODEL, null=True, blank=True,
                        on_delete=SET_NULL, related_name='visual_cells',
                        verbose_name=_("Artist for this Part of the Canvas"),)
    x_position = IntegerField(_("Horizontal position relative to 0"))
    y_position = IntegerField(_("Veritical position relative to 0"))
    is_editable = BooleanField(_("Whether artists are allowed to edit this "
                                 "cell."), default=True)

    class Meta:

        """Enforce efficiency and correctness within each canvas."""

        unique_together = (("canvas", "artist"),
                           ("canvas", "x_position", "y_position"))

    def clean(self):
        """Means of testing if cell is outside a pre-defined grid."""
        if (self.canvas.grid_height and
                not self.canvas.grid_width > self.x_position >= 0 or
                not self.canvas.grid_height > self.y_position >= 0):
            raise ValidationError(_(f'Cell position {self.coordinates} is '
                                    'outside the grid'))

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

    def __str__(self):
        return (
            f'({self.x_position}, {self.y_position}) '
            f'{self.canvas} - '
            f'{self.artist.username if self.artist else "Not assigned"}'
        )

    def default_blank_list(self):
        return [0 for x in range(self.canvas.cell_divisions)]

    def set_blank(self):
        blank_list = self.default_blank_list()
        self.cell_edits.create(edges_horizontal=blank_list,
                               edges_vertical=blank_list,
                               edges_south_east=blank_list,
                               edges_south_west=blank_list)

    def get_neighbours(self, as_tuple=False):
        """
        Return Moore's neighbours, including torus neighbours if appropriate.
        """
        neighbours = {}
        for direction, coordinate_difference in CELL_NEIGHBOURS.items():
            coords = (self.x_position + coordinate_difference[0],
                      self.y_position + coordinate_difference[1])
            if self.canvas.is_torus:
                coords = self.canvas.correct_coordinates_for_torus(coords)
            try:
                neighbour = self.canvas.visual_cells.get(x_position=coords[0],
                                                         y_position=coords[1])
            except VisualCell.DoesNotExist:
                neighbour = None
            if neighbour and as_tuple:
                neighbours[direction] = neighbour.coordinates
            else:
                neighbours[direction] = neighbour
        return neighbours

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
    #         self.cell_edits = [self.blank_cell()]
    #     super().save(*args, **kwargs)


class VisualCellEdit(Model):

    """Timestamped edits to cells."""

    cell = ForeignKey(VisualCell, on_delete=CASCADE, related_name="cell_edits")
    timestamp = DateTimeField(auto_now=True)
    edges_horizontal = ArrayField(PositiveSmallIntegerField())
    edges_vertical = ArrayField(PositiveSmallIntegerField())
    edges_south_east = ArrayField(PositiveSmallIntegerField())
    edges_south_west = ArrayField(PositiveSmallIntegerField())

    def __str__(self):
        state = f'self.cell.artist ' if self.cell.artist else 'Empty '
        return state + f'timestamp'
