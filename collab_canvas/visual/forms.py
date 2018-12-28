from django.forms import ModelForm
from .models import VisualCanvas


class VisualCanvasForm(ModelForm):

    """Form for editing a cell on a canvas."""

    class Meta:

        model = VisualCanvas

    # def clean_x_position(self, *args, **kwargs):
    #     """
    #     Ensure x position is within grid or adjacent if canvas is dynamic.
    #
    #     If canvas is dynamic ensure
    #     """
