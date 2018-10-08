from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
#from django.shortcuts import render

# Create your views here.


@method_decorator(login_required, name='dispatch')
class VisualView(TemplateView):

    """Presents a visual canvas for collaboration."""

    template_name = 'pages/visual_canvas.html'
