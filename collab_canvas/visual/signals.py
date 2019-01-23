from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VisualCanvas, VisualCell, VisualCellEdit


@receiver(post_save, sender=VisualCanvas)
def initialize_canvas(sender, **kwargs):
    """
    Initiate VisualCells if canvas grid_width or grid_height are set > 0.
    """
    if kwargs['created'] and (kwargs['instance'].grid_width or
                              kwargs['instance'].grid_height):
        kwargs['instance'].generate_grid()


@receiver(post_save, sender=VisualCell)
def initialize_and_manage_cell_edits(sender, **kwargs):
    """Initiate a blank VisualCellEdit when creating a VisualCell."""
    if kwargs['created']:
        cell = kwargs['instance']
        if cell.is_editable and cell.canvas.new_cells_allowed:
            edges = cell.get_blank_with_neighbour_edges()
            cell.edits.create(**edges)
        else:
            cell.set_blank()


@receiver(post_save, sender=VisualCellEdit)
def apply_edge_changes_to_neighbours(sender, **kwargs):
    """
    Dispatch overlapping edge edits to adjacent VisualCells.

    Todo:
        * Consider allowing automated edits to neighbours as well
    """
    if kwargs['created']:
        cell_edit = kwargs['instance']
        cell_edit.cell.dispatch_neighbour_edits()
