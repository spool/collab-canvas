from django.contrib.admin import ModelAdmin, register
from .models import VisualCanvas


# Register your models here.
@register(VisualCanvas)
class VisualCanvasAdmin(ModelAdmin):

    """Admin for creating and managing VisualCanvas runs."""

    list_display = ('title', 'slug', 'creator', 'start_time', 'end_time')
    prepopulated_fields = {"slug": ("title",)}
