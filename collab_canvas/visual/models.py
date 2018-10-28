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
                              DateTimeField, ForeignKey, Model,
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
    cell. If a torus then a grid length must be defined. If not a torus then a
    grid_length will enforce the maximum edges but not connect edge neighbours.
    If grid length is not defined then the canvas will grow with positive and
    negative coordinates organically with each new artist.
    """

    title = CharField(_("Canvas Title"), max_length=100)
    slug = SlugField(_("URL Compliant Title"), unique=True)
    description = TextField(max_length=200, blank=True)
    start_time = DateTimeField(_("Start Time of Public Canvas Editing"))
    end_time = DateTimeField(_("Time the Canvas Will Stop Accepting Edits"))
    grid_length = PositiveSmallIntegerField(
        _("Torus grid length, where max number of cells is this squared. "
          "If null, cells will spread."),
        default=8,  # Default assumes a square grid
        blank=True, null=True)
    cell_divisions = PositiveSmallIntegerField(_("Cell Divisions"), default=8)
    creator = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE,
                         verbose_name=_("Person who created this Visual "
                                        "Canvas"))
    is_torus = BooleanField(_("Initialize a torus grid that can't be changed"))

    def __str__(self):
        return f'{self.title} ends {self.end_time:%Y-%m-%d %H:%M}'

    def clean(self):
        if self.is_torus and self.grid_length is None:
            raise ValidationError(_('Torus VisualCanvases must have a length'))

    def generate_grid(self):
        """Generate a torus grid."""
        for x in range(self.grid_length):
            for y in range(self.grid_length):
                self.visual_cells.create(x_position=x, y_position=y)

    @property
    def max_coordinates(self):
        """
        Maximum point for torus grid.

        Note:
            * Implemented in case of future non-square (use grid_width if so).
        """
        if self.grid_length is None:
            raise ValidationError(_('Max of coordinates requires a defined'
                                    'length'))
        return (self.grid_length - 1, self.grid_length - 1)

    def get_centre_cell_coordinates(self):
        """Return the centre most cell max x, max y points."""
        if self.grid_length:
            return (self.max_coordinates[0]//2, self.max_coordinates[1]//2)
        else:
            return (0, 0)

    def get_random_cell_coordinates(self):
        """
        Get pure random cell (possibly just coordinates of) from canvas.

        For non grid cnavasas this might be annoyingly slow.
        """
        if self.grid_length:  # Note: must add 1 to include max coordinate
            return (choice(list(range(self.max_coordinates[0] + 1))),
                    choice(list(range(self.max_coordinates[1] + 1))))
        else:
            self.visual_cells.order_by('?').first().coordinates

    def correct_coordinates_for_torus(self, coordinates):
        """
        Enforce coordinates for a torus grid.

        This method projects negative coordinates to positive ones. Requires
        a torus of length >= 3.

        Todo:
            * Rewrite to more efficiently handle type issues.
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

    def get_or_create_contiguous_cell(self, first_cell_algorithm='centre'):
        """
        Find a continguous cell that's not owned

        Todo:
            * May be applicable to torus **and** organic growth
            * Test algorithm dict method
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
            if not self.grid_length and not self.is_torus:
                return self.visual_cells.create(x_position=0, y_position=0)
            else:
                coords = getattr(
                    self, self.INITIAL_CELL_METHODS[first_cell_algorithm])()
                return self.visual_cells.get(x_position=coords[0],
                                             y_position=coords[1])
        coordinate_differences = list(CELL_ADJACENTS.values())
        shuffle(allocated_cells)
        for cell in allocated_cells:
            shuffle(coordinate_differences)
            for coordinate_difference in coordinate_differences:
                potential_cell = (cell[0] + coordinate_difference[0],
                                  cell[1] + coordinate_difference[1])
                if potential_cell not in allocated_cells:  # Might choose a pre-allocated cell
                    if not self.grid_length:
                        return self.visual_cells.add(
                            x_position=potential_cell[0],
                            y_position=potential_cell[1])
                    if self.is_torus:
                        potential_cell = self.correct_coordinates_for_torus(
                            potential_cell)
                    try:
                        blank_cell = self.visual_cells.get(
                            x_position=potential_cell[0],
                            y_position=potential_cell[1])
                        assert blank_cell.artist is None
                        return blank_cell
                    except VisualCell.DoesNotExist:
                        raise VisualCell.DoesNotExist(_("No cell of that position"))
                    except AssertionError:
                        raise ValidationError(_("That cell is already owned by"
                                                "another artist"))

    def save(self, *args, **kwargs):
        """
        Save VisualCanvas, enforcing slug creation and torus if selected.

        Todo:
            * Consider if it's worth initiating a first cell when not a torus.
        """
        if not self.id:
            self.slug = slugify(self.title)
            # if self.grid_length:
            #     self.generate_grid()
            #     # self.initiate_torus_links()
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
    y_position = IntegerField()
    x_position = IntegerField()

    def clean(self):
        if (self.canvas.grid_length and
                not self.canvas.grid_length > self.x_position > 0 or
                not self.canvas.grid_length > self.y_position > 0):
            raise ValidationError(_('Cell position is outside the grid'))

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
            f'{self.artist.name if self.artist else "Not assigned"}'
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
