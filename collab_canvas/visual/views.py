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
from django.views.generic import UpdateView, DetailView, TemplateView
# BaseView, RedirectView
from django.shortcuts import get_object_or_404, redirect, reverse
# from django.shortcuts import render

from .models import VisualCanvas, VisualCell, VisualCellEdit
# from .forms import VisualCellEditForm


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

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            if request.user.is_authenticated:
                cell = self.get_object().get_or_assign_cell(request.user)
                return redirect('visual:cell-edit', cell_id=cell.id)
            else:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
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

    def dispatch(self, request, *args, **kwargs):
        """Show cell or forward if not passing test_func."""
        user_test_result = self.get_test_func()()
        if not user_test_result:
            if request.user.is_authenticated:
                cell = self.get_object()
                if request.user == cell.artist:
                    # Force cell artist to only edit cell, not view
                    return redirect('visual:cell-edit', cell_id=cell.id)
                else:
                    # Get or assign cell if artist is not the owner
                    cell = cell.canvas.get_or_assign_cell(request.user)
                    return redirect('visual:cell-edit', cell_id=cell.id)
            else:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        """Check if user has access to viewing the canvas."""
        user = self.request.user
        if user.is_authenticated:
            return (user.is_superuser or
                    user == self.get_object().canvas.creator)
        return False


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
        queryset = super().get_queryset()
        return queryset.filter(cell__pk=self.kwargs.get('cell_id'))

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        for cell_edit in queryset:
            if cell_edit.history_number is self.kwargs.get('cell_history'):
                return cell_edit
        raise Http404()


class VisualCellValidEditView(VisualCellEditHistoryView):

    """View a saved is_valid edit of an assigned cell."""

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        for cell_edit in queryset:
            if cell_edit.edit_number is self.kwargs.get('edit_number'):
                return cell_edit
        raise Http404()


class VisualCellEditView(UserPassesTestMixin, UpdateView):

    """
    Core view for collaborative cell editing.

    In its present form, this view is designed to support collaborative edit
    with adjacent neighbours---east, south, north, west---on the edge. This
    means that any edit of edge must also be applied to neighbours. The goal is
    for this to sufficiently work with Django Channels and websockets, but a
    fallback may be needed.
    """

    template_name = 'visual/visual_cell.html'
    model = VisualCellEdit
    # form = VisualCellEditForm

    permission_denied_message = ('only administators, the canvas creator and '
                                 'cell owner can edit a cell')
    context_object_name = 'visual_cell_edit'
    fields = VisualCellEdit.get_edge_names()

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(cell__pk=self.kwargs.get('cell_id'))

    # def get_object(self, queryset=None):
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #     last_cell_edit = queryset.filter(is_valid=True).last()
    #     # If no history is available, queryset returns None
    #     if last_cell_edit:
    #         last_cell_edit.id = None
    #         last_cell_edit.artist = self.request.user
    #         return last_cell_edit
    #     raise Http404()

    # def _get_latest_cell_edit(self, pk_url_kwarg='cell_id'):
    #     """Return parent cell."""
    #     cell =
    #     return cell.latest_valid_edit

    def _get_cell(self, pk_url_kwarg: str = 'cell_id'):
        """Query for parent cell."""
        self.cell = get_object_or_404(VisualCell,
                                      pk=self.kwargs.get(pk_url_kwarg))

    def _get_latest_valid_edit(self):
        """Query for latest_valid_edit, generating a new one if necessary."""
        if not hasattr(self, 'cell'):
            self._get_cell()
        try:
            self.latest_valid_edit = self.cell.latest_valid_edit
        except VisualCellEdit.DoesNotExist:
            edges = self.cell.get_blank_with_neighbour_edges()
            # Note: we do not assign an artist to the intial design because
            # it is autogenerated, not the artist's creative choice
            self.latest_valid_edit = self.cell.edits.create(**edges)

    def test_func(self):
        """Check if user has access to edit the cell."""
        user = self.request.user
        if user.is_authenticated:
            if not hasattr(self, 'cell'):
                self._get_cell()
            # Todo: cache these queries for efficiency
            return (user.is_superuser or
                    user == self.cell.artist or
                    user == self.cell.canvas.creator)
        return False

    # def get_initial(self):
    #     """Add last most recent cell_edit data as starting point."""
    #     initial = super().get_initial()
    #     if not hasattr(self, 'latest_valid_edit'):
    #         self._get_latest_valid_edit()
    #     for field in self.fields:
    #         initial[field] = getattr(self.latest_valid_edit, field)
    #     return initial

    # def clean(self):
    #     """Override to expand the clean method."""
    #     new_cell_edit = super().clean()
    #     if not hasattr(self, 'cell'):
    #         self._get_cell()
    #     new_cell_edit.cell = self.cell
    #     return new_cell_edit

    # def form_valid(self, form):
    #     """Add artist and cell to form for validation."""
    #     form.instance.artist = self.request.user
    #     if not hasattr(self, 'cell'):
    #         self._get_cell()
    #     form.instance.cell = self.cell
    #     return super().form_valid(form)

    # self._get_latest_cell_edit(pk_url_kwarg='cell_id')

    def dispatch(self, request, *args, **kwargs):
        """Show cell or forward if not passing test_func."""
        user_test_result = self.get_test_func()()
        if not user_test_result:
            if request.user.is_authenticated:
                # # Todo: Check this for efficiency
                # if not hasattr(self, 'cell'):
                #     self._get_cell()
                cell = self.cell.canvas.get_or_assign_cell(request.user)
                # cell = get_object_or_404(VisualCell,
                #                          pk=self.kwargs.get('cell_id'))
                return redirect('visual:cell-edit', cell_id=cell.id)
            else:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # def get_form(self, request, obj=None, **kwargs):
    #     if not hasattr(self, 'cell'):
    #         self._get_cell()
    #     kwargs['cell'] = self.cell
    #     return super().get_form(request, obj, **kwargs)

    def form_valid(self, form):
        # form.instance.cell_id = self.kwargs.get('cell_id')
        form.instance.artist = self.request.user
        return super().form_valid(form)

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['artist'] = self.request.user
    #     return kwargs

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     if not self.cell:
    #         self._get_cell()
    #     kwargs['cell']

    # def get_object(self, queryset=None):
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #     if not hasattr(self, 'latest_edit'):
    #         self._get_latest_cell_edit()
    #     new_cell_edit = self.latest_edit
    #     new_cell_edit.id = None
    # #     # Needed because case admin or canvas creators may need to edit
    #     new_cell_edit.artist = self.request.user
    #     return new_cell_edit

    # def post(self, request, *args, **kwargs):
    #     form = self.get_form()
    #     assert False
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         assert False
    #         return self.form_invalid(form)
        # self.object = self.get_object()
        # self.object.id = None
        # self.object.artist = request.user
        # return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        assert False

    def get_object(self, queryset=None):
        if not hasattr(self, 'latest_valid_edit'):
            self._get_latest_valid_edit()
        if not self.latest_valid_edit:
            # This should only occur if all existing edits are marked invalid
            initial_edges = self.cell.get_blank_with_neighbour_edges()
            self.latest_valid_edit = self.cell.edits.create(**initial_edges)
        new_edit = self.latest_valid_edit
        new_edit.id = None
        return new_edit
        # return new_edit
        # else:
        #     new_edit = self.latest_valid_edit
        #     new_edit.id = None
        #     raise Http404()
        # return self.latest_valid_edit

    def get_success_url(self):
        """Return successful url redirect."""
        return reverse('visual:cell-edit-success',
                       kwargs={'cell_id': self.object.cell.id})


class VisualCellEditSuccessView(TemplateView):

    """Confirm cell edit success."""

    template_name = 'visual/visual_cell.html'
