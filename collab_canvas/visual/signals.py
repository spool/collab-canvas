from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import VisualCanvas, VisualCell


@receiver(post_save, sender=VisualCanvas)
def initialize_canvas(sender, **kwargs):
    """Initiate VisualCells if canvas grid_length is set."""
    if kwargs['created'] and kwargs['instance'].grid_length:
        kwargs['instance'].generate_grid()


@receiver(post_save, sender=VisualCell)
def initialize_blank_cell(sender, **kwargs):
    """Initiate a blank VisualCellEdit when creating a VisualCell."""
    if kwargs['created']:
        kwargs['instance'].set_blank()
