# from django.contrib.auth.decorators import login_required

# from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
# from django.shortcuts import render

# Create your views here.


# @method_decorator(login_required, name='dispatch')
class VisualView(LoginRequiredMixin, TemplateView):

    """Presents a visual canvas for collaboration."""

    template_name = 'pages/visual_canvas.html'

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
