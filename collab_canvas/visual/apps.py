from django.apps import AppConfig


class VisualConfig(AppConfig):

    name = 'collab_canvas.visual'
    verbose_name = "Visual Collaboration"

    def ready(self):
        try:
            from . import signals  # noqa F401
        except ImportError:
            pass
