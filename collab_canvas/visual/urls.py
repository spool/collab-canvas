"""
URL structure for VisualCanvases.

Basic structure:
/visual/canvas-uuid/cell-uuid/edits
/visual/create?

Todo:
    * Ensure
"""
from django.urls import path
from .views import VisualCanvasView, VisualCellView, VisualCellEdit


app_name = "visual"  # Required for naming urls


urlpatterns = [
    # path("", VisualView.as_view(), name="visual"),
    # path("current/", VisualView.as_view(), name="current")
    path("canvas/<uuid:canvas_id>/<uuid:cell_id>/<int:edit_number>/",
         VisualCellEdit.as_view(),
         name="cell-edit"),  # This should only be visible to managers
    path("canvas/<uuid:canvas_id>/<uuid:cell_id>/", VisualCellView.as_view(),
         name="cell"),
    path("canvas/<uuid:canvas_id>/", VisualCanvasView.as_view(), name="canvas"),
]
