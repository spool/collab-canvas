# from django.contrib.auth.decorators import login_required

# from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
# from django.shortcuts import render

from .models import VisualCanvas, VisualCell, VisualCellEdit


# @method_decorator(login_required, name='dispatch')
class VisualCanvasView(LoginRequiredMixin, CreateView):

    """Presents a visual canvas for collaboration."""

    template_name = 'pages/visual_canvas.html'
    model = VisualCanvas


class VisualCellView(LoginRequiredMixin, CreateView):

    """Creates a new cell or assigns ownership to a pre-existing one."""

    template_name = 'pages/visual_cell.html'
    model = VisualCell


class VisualCellEdit(LoginRequiredMixin, CreateView):

    """View for editing an assigned cell."""

    template_name = 'pages/visual_cell_edit.html'
    model = VisualCellEdit


#     def get_context_data(self, **kwargs):
#         """Basic return of cell for current canvas, or generate new test."""
#         if

# from django.contrib.auth import get_user_model
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse
# from django.views.generic import DetailView, ListView, RedirectView, UpdateView
#
# User = get_user_model()
#
#
# class UserDetailView(LoginRequiredMixin, DetailView):
#
#     model = User
#     slug_field = "username"
#     slug_url_kwarg = "username"
#
#
# user_detail_view = UserDetailView.as_view()
#
#
# class UserListView(LoginRequiredMixin, ListView):
#
#     model = User
#     slug_field = "username"
#     slug_url_kwarg = "username"
