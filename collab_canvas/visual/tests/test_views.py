from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from .views import VisualView
from .utils import BaseVisualTest, CanvasFactory, UserFactory


class TestVisualCanvasView(BaseVisualTest):

    """Test basic browser interaction."""

    def setUp(self):
        """Generate simple 3x3 torus grid for tests."""

    def test_get_redirect_url(
        self, user: UserFactory, request_factory: RequestFactory
    ):
        view = VisualView()
        request = request_factory.get("/fake-url")
        request.user = user

        view.request = request

        self.assertEqual(view.get_redirect_url(),
                         f"/canvas/{request.canvas}/{user.username}/")
