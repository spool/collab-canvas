"""
URL structure for VisualCanvases.

Basic structure:
/visual/canvas-uuid/cell-uuid/edits
/visual/create?



Todo:
    * Ensure permission applies for each path
"""
from django.urls import path
from .views import (VisualCanvasView, VisualCellView, VisualCellEditView,
                    VisualCellEditHistoryView)


app_name = "visual"  # Required for naming urls


urlpatterns = [
    # path("", VisualView.as_view(), name="visual"),
    # path("current/", VisualView.as_view(), name="current")

    # path("", VisualCellEdit.as_view(), name="featured-canvas")
    # path("/canvas/")

    # These should only be visible to managers
    path("canvas/<uuid:canvas_id>/", VisualCanvasView.as_view(), name="canvas"),
    # possibly the one view for participants
    path("canvas/cell/<uuid:cell_id>/", VisualCellView.as_view(), name="cell"),
    # the rest only for managers
    path("canvas/cell/<uuid:cell_id>/<int:edit_number>/",
         VisualCellEditView.as_view(),
         name="cell-edit"),
    path("canvas/cell/<uuid:cell_id>/history/<int:cell_history>/",
         VisualCellEditHistoryView.as_view(),
         name="cell-history"),
]
