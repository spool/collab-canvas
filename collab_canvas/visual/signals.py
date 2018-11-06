from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VisualCanvas, VisualCell


@receiver(post_save, sender=VisualCanvas)
def initialize_canvas(sender, **kwargs):
    """
    Initiate VisualCells if canvas grid_width or grid_height are set > 0.
    """
    if kwargs['created'] and (kwargs['instance'].grid_width or
                              kwargs['instance'].grid_height):
        kwargs['instance'].generate_grid()


@receiver(post_save, sender=VisualCell)
def initialize_blank_cell(sender, **kwargs):
    """Initiate a blank VisualCellEdit when creating a VisualCell."""
    if kwargs['created']:
        kwargs['instance'].set_blank()
