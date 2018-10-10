from config.settings.base import AUTH_USER_MODEL

from django.contrib.postgres.fields import ArrayField
from django.db.models import (CASCADE, SET_NULL, CharField, DateTimeField,
                              ForeignKey, Model, PositiveSmallIntegerField,
                              SlugField, TextField)
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class VisualCanvas(Model):

    """
    Canvas for visual collaboration.

    Each canvas has a start and end date, and normal users may only edit one
    cell.
    """

    title = CharField(_("Canvas Title"), max_length=100)
    slug = SlugField(_("URL Compliant Title"), unique=True)
    description = TextField(max_length=200, blank=True)  # Only enforced in admin interface, not in database
    start_time = DateTimeField(_("Start Time of Public Canvas Editing"))
    end_time = DateTimeField(_("Time the Canvas Will Stop Accepting Edits"))
    grid_length = PositiveSmallIntegerField(
        _("The Total Grid Size is this squared"), default=8)  # Assumes a square grid
    cell_divisions = PositiveSmallIntegerField(_("Cell Divisions"), default=8)
    creator = ForeignKey(AUTH_USER_MODEL, null=True, on_delete=SET_NULL)  # _("Person who created this Visual Canvas")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class VisualCell(Model):

    """A cell in a VisualCanvas."""

    canvas = ForeignKey(VisualCanvas, on_delete=CASCADE)  # _("Canvas Cell is Associated With"),
    artist = ForeignKey(AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL)
                                                      # Initial grid won't have users assigned
                                                      # _("Artist for this Part of the Canvas"),
    vertical_place = PositiveSmallIntegerField()
    horizontal_place = PositiveSmallIntegerField()

    north = ForeignKey('VisualCell', related_name="south_cell", blank=True,
                       null=True, on_delete=SET_NULL)
    north_east = ForeignKey('VisualCell', related_name="south_west_cell",
                            blank=True, null=True, on_delete=SET_NULL)
    east = ForeignKey('VisualCell', related_name="west_cell", blank=True,
                      null=True, on_delete=SET_NULL)
    south_east = ForeignKey('VisualCell', related_name="north_west_cell",
                            blank=True, null=True, on_delete=SET_NULL)
    south = ForeignKey('VisualCell', related_name="north_cell", blank=True,
                       null=True, on_delete=SET_NULL)
    south_west = ForeignKey('VisualCell', related_name="north_east_cell",
                            blank=True, null=True, on_delete=SET_NULL)
    west = ForeignKey('VisualCell', related_name="east_cell", blank=True,
                      null=True, on_delete=SET_NULL)
    north_west = ForeignKey('VisualCell', related_name="south_east_cell",
                            blank=True, null=True, on_delete=SET_NULL)

    def __str__(self):
        return (
            f'({self.vertical_place}, {self.horizontal_place}) '
            f'{self.canvas} - {self.artist.name}'
        )

    def default_blank_list():
        return [o for x in self.canvas.cell_divsions]

    def default_blank_cell():
        return VisualCellEdit(
            edges_horizontal=self.default_blank_list(),
            edges_vertical=self.default_blank_list(),
            edges_south_east=self.default_blank_list(),
            edges_south_west=self.default_blank_list(),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.cell_visual_edit_set.add(self.default_blank_cell())
        super().save(*args, **kwargs)


class VisualCellEdit(Model):

    """Timestamped edits to cells."""

    cell = ForeignKey(VisualCell, on_delete=CASCADE)
    timestamp = DateTimeField(auto_now=True)
    edges_horizontal = ArrayField(PositiveSmallIntegerField())
    edges_vertical = ArrayField(PositiveSmallIntegerField())
    edges_south_east = ArrayField(PositiveSmallIntegerField())
    edges_south_west = ArrayField(PositiveSmallIntegerField())

    def __str__(self):
        return f'{self.artist} edit at {self.timestamp}'
