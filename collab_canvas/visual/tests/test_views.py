from unittest import expectedFailure, skip

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from ..views import VisualCanvasView
from .utils import BaseVisualTest, CanvasFactory, UserFactory


class TestDynamicVisualCanvasView(BaseVisualTest):

    """Test basic browser interaction."""

    def setUp(self):
        """Generate simple 3x3 torus grid for tests."""
        super().setUp()
        self.anon_user = AnonymousUser()
        self.request_factory = RequestFactory()
        self.view = VisualCanvasView()
        self.canvas = CanvasFactory(
            title='Test Dynamic Canvas',
            grid_height=0,
            grid_width=0,
            new_cells_allowed=True)

    @expectedFailure
    def test_get_user_redirect_url(self):
        request = self.request_factory.get("/fake-url")
        request.user = UserFactory()

        self.view.request = request

        self.assertEqual(self.view.get_redirect_url(),
                         f"/canvas/{request.canvas}/{request.user.username}/")

    @skip
    def test_assign_first_dynamic_cell(self):
        pass
