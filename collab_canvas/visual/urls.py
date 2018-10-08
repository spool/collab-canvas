from django.urls import path
from .views import VisualView


urlpatterns = [
    path("", VisualView.as_view(), name="visual"),
]
