"""
Structure views for creating, observing, and editing canvases.

A basic structure for viewing different sections of visual canvases, dependent
in part on permissions.

    path("canvas/<uuid:canvas_id>/", VisualCanvasView.as_view(), name="canvas"),
    # possibly the one view for participants
    path("canvas/<uuid:canvas_id>/<uuid:cell_id>/", VisualCellView.as_view(),
         name="cell"),
    # the rest only for managers
    path("canvas/<uuid:canvas_id>/<uuid:cell_id>/<int:edit_number>/",
         VisualCellEdit.as_view(),
         name="cell-edit"),
    path("canvas/<uuid:canvas_id>/<uuid:cell_id>/history/<int:cell_history>/",
         VisualCellEdit.as_view(),
         name="cell-history"),


""                      Just
                        or redirect if not owner/manager
                        if has login:
                            if assigned cell:
                                redirect to canvas/canvas_id/cell_id/edit
                            else:
                                assign cell
                                redirect to canvas/canvas_id/cell_id/edit
                        else:
                            redirect to generate account

canvas/                     Initially

{% if perms.app_label.can_do_something %}
<form here>
{% endif %}
so...

{% if perms.visual.canvas_owner %}

{% endif %}

canvas/                     Initially forward to currently active canvas
                            Possibly have a way of specifying which of current
                            tests to forward to

                            Future: if correct permission see list of all
                            canvas in reverse date order of start

                            (or just canvas/list...)


canvas/<canvas_id>/          view canvas
                                (eventually allow edits for some on this page...?)
                                (permission to see view, the permission within
                                template for editing)
                                {% if perms.app_label.can_do_something %}
                                <form here>
                                {% endif %}
                                so...
                                {% if perms.visual.canvas_owner %}
                                {% endif %}
                            or redirect if not owner/manager
                            if has login:
                                if assigned cell:
                                    redirect to canvas/canvas_id/cell_id/edit
                                else:
                                    assign cell
                                    redirect to canvas/canvas_id/cell_id/edit
                            else:
                                redirect to generate account

canvas/<canvas_id>/<cell_id>/ view cell (similar to permission above)
"""
# from django.contrib.auth.decorators import login_required

# from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
# from django.utils.decorators import method_decorator
from django.http import Http404
from django.views.generic import DetailView  # BaseView, RedirectView
# from django.views.generic.edit import CreateView, DetailView  # BaseView, RedirectView
# from django.shortcuts import get_object_or_404
# from django.shortcuts import render

from .models import VisualCanvas, VisualCell, VisualCellEdit


# @method_decorator(login_required, name='dispatch')
class VisualCanvasView(UserPassesTestMixin, DetailView):

    """Presents a visual canvas for collaboration."""

    template_name = 'visual/visual_canvas.html'
    model = VisualCanvas
    context_object_name = 'visual_canvas'
    # permission_required = 'visual.view_visualcanvas'
    # raise_exception = False  # Consider setting this to True
    permission_denied_message = ('only administators and the canvas creator may '
                                 'view this canvases')
    pk_url_kwarg = 'canvas_id'

    def test_func(self):
        """Check if user has access to viewing the canvas."""
        user = self.request.user
        return user.is_superuser or user == self.get_object().creator

    # def get_object(self):
    #     """Return canvas specified or 404."""
    #     return get_object_or_404(VisualCanvas, id=self.kwargs['canvas_id'])


class VisualCellView(UserPassesTestMixin, DetailView):

    """Shows a cell or assigns ownership to a pre-existing one."""

    template_name = 'visual/visual_cell.html'
    model = VisualCell
    context_object_name = 'visual_cell'
    # permission_required = 'visual.view_visualcell'
    permission_denied_message = ('only administators, the canvas creator and '
                                 'the cell artist may view this cell')
    pk_url_kwarg = 'cell_id'

    def test_func(self):
        """Check if user has access to viewing the canvas."""
        user = self.request.user
        return (user.is_superuser or user == self.get_object().artist or
                user == self.get_object().canvas.creator)


class VisualCellEditHistoryView(UserPassesTestMixin, DetailView):

    """View a saved edit of an assigned cell."""

    template_name = 'visual/visual_cell.html'
    model = VisualCellEdit
    context_object_name = 'visual_cell_edit'
    # permission_required = 'visual.view_visualcelledit'
    permission_denied_message = ('only administators may view cell history')
    # slug_url_kwarg

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = super(VisualCellEditHistoryView, self).get_queryset()
        return queryset.filter(cell__pk=self.kwargs.get('cell_id'))

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        for cell_edit in queryset:
            if cell_edit.history_number is self.kwargs.get('cell_history'):
                return cell_edit
        raise Http404()


class VisualCellEditView(VisualCellEditHistoryView):

    """View a saved is_valid edit of an assigned cell."""

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        for cell_edit in queryset:
            if cell_edit.edit_number is self.kwargs.get('edit_number'):
                return cell_edit
        raise Http404()
