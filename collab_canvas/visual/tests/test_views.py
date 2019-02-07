# from unittest import expectedFailure

# from django.contrib.auth.models import AnonymousUser
# from django.test import RequestFactory
from django.urls import reverse

from ..views import VisualCanvasView
from .utils import (BaseVisualTest, CanvasFactory, CellFactory,
                    CellEditFactory, UserFactory, TEST_USER_PASSWORD)


class BaseDynamicCanvasTest(BaseVisualTest):

    """Basic test setUp for Canvases."""

    def setUp(self):
        """Generate simple 3x3 torus grid for tests."""
        super().setUp()
        # self.anon_user = AnonymousUser()
        # self.request_factory = RequestFactory()
        self.view = VisualCanvasView()
        self.canvas = CanvasFactory(
            title='Test Dynamic Canvas',
            grid_height=0,
            grid_width=0,
            new_cells_allowed=True)


class TestDynamicVisualCanvasViews(BaseDynamicCanvasTest):

    """Test basic browser interaction."""

    def test_login_redirect(self):
        response = self.client.get(self.canvas.get_absolute_url(), follow=True)
        self.assertEqual(
            response.redirect_chain[0],
            ('/accounts/login/?next=' + self.canvas.get_absolute_url(), 302)
        )
        self.assertEqual(response.status_code, 200)

    def test_super_user_privilege(self):
        """Test that super_users can view canvases by default."""
        super_user = self.canvas.creator
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.canvas.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_canvas'].title,
                         self.canvas.title)

    def test_standard_user_privileges(self):
        """Test that cannot view canvases by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.canvas.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        self.canvas.creator = user
        self.canvas.save()
        response = self.client.get(self.canvas.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_canvas'].title,
                         self.canvas.title)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = self.canvas.creator
        response = self.client.get("/canvas/bad-n00m835", follow=True)
        self.assertEqual(response.status_code, 404)


class TestDynamicVisualCanvasCellView(BaseDynamicCanvasTest):

    """Test CanvasCellView manages to show cells adhering to permission."""

    def setUp(self):
        """Add a single cell on top of canvas to test view."""
        super().setUp()
        self.cell = CellFactory(canvas=self.canvas)

    def test_login_redirect(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(self.cell.get_absolute_url(), follow=True)
        self.assertEqual(
            response.redirect_chain[0],
            ('/accounts/login/?next=' + self.cell.get_absolute_url(), 302)
        )
        self.assertEqual(response.status_code, 200)

    def test_super_user_privilege(self):
        """Test super_users can view cells by default."""
        super_user = self.canvas.creator
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell'].coordinates,
                         self.cell.coordinates)

    def test_standard_user_privileges(self):
        """Test that cannot view celles by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        self.cell.artist = user
        self.cell.save()
        response = self.client.get(self.cell.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell'].coordinates,
                         self.cell.coordinates)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = self.cell.artist
        response = self.client.get("/cell/bad-n00m835", follow=True)
        self.assertEqual(response.status_code, 404)


class TestDynamicVisualCanvasCellEditHistoryView(BaseDynamicCanvasTest):

    """Test CanvasCellView manages to show cells adhering to permission."""

    def setUp(self):
        """Add a single cell on top of canvas to test view."""
        super().setUp()
        self.cell_edit = CellEditFactory(cell=CellFactory(canvas=self.canvas))

    def test_login_redirect(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(self.cell_edit.get_absolute_url(),
                                   follow=True)
        self.assertEqual(
            response.redirect_chain[0],
            ('/accounts/login/?next=' + self.cell_edit.get_absolute_url(), 302)
        )
        self.assertEqual(response.status_code, 200)

    def test_super_user_privilege(self):
        """Test super_users can view cells by default."""
        super_user = self.canvas.creator
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell_edit.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell_edit'].edges_horizontal,
                         [0]*12)

    def test_standard_user_privileges(self):
        """Test that cannot view celles by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell_edit.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        self.cell_edit.cell.artist = user
        self.cell_edit.artist = user
        self.cell_edit.cell.save()
        response = self.client.get(self.cell_edit.get_absolute_url())
        self.assertEqual(response.status_code, 403)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = self.canvas.creator
        response = self.client.get(self.cell_edit.get_absolute_url() + '3',
                                   follow=True)
        self.assertEqual(response.status_code, 404)


class TestDynamicVisualCanvasCellEditValidView(BaseDynamicCanvasTest):

    """Test CanvasCellView manages to show cells adhering to permission."""

    def setUp(self):
        """Add a single cell on top of canvas to test view."""
        super().setUp()
        self.cell_edit = CellEditFactory(cell=CellFactory(canvas=self.canvas))
        self.url = reverse('visual:cell-edit',
                           kwargs={'cell_id': self.cell_edit.cell.id,
                                   'edit_number': self.cell_edit.edit_number})

    def test_login_redirect(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.redirect_chain[0],
                         ('/accounts/login/?next=' + self.url, 302))
        self.assertEqual(response.status_code, 200)

    def test_super_user_privilege(self):
        """Test super_users can view cells by default."""
        super_user = self.canvas.creator
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell_edit'].edges_horizontal,
                         [0]*12)

    def test_standard_user_privileges(self):
        """Test that cannot view celles by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.cell_edit.cell.artist = user
        self.cell_edit.artist = user
        self.cell_edit.cell.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = self.canvas.creator
        response = self.client.get(self.url + '3', follow=True)
        self.assertEqual(response.status_code, 404)
