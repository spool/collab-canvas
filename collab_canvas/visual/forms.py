from django.forms import ModelForm
from .models import VisualCellEdit


class VisualCellEditForm(ModelForm):

    """Form for editing a cell on a canvas."""

    class Meta:

        model = VisualCellEdit
        fields = VisualCellEdit.get_edge_names()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.artist = kwargs['artist']

    # def __init__(self, cell_id, artist_id,)

    # def clean_x_position(self, *args, **kwargs):
    #     """
    #     Ensure x position is within grid or adjacent if canvas is dynamic.
    #
    #     If canvas is dynamic ensure
    #     """
