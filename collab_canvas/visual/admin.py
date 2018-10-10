from django.contrib.admin import ModelAdmin
from .models import VisualCanvas

# Register your models here.
class VisualCanvas(ModelAdmin):

    """Admin for creating and managing VisualCanvas runs."""

    list_display = ('title', 'creator', 'start_time', 'end_time')
