# from unittest import expectedFailure

# from django.contrib.auth.models import AnonymousUser
# from django.test import RequestFactory
from django.urls import reverse

from .utils import (BaseVisualTest, CanvasFactory, CellFactory,
                    CellEditFactory, SuperUserFactory, UserFactory,
                    TEST_USER_PASSWORD)


class BaseDynamicCanvasTest(BaseVisualTest):

    """Basic test setUp for Canvases."""

    def setUp(self):
        """Generate simple 3x3 torus grid for tests."""
        super().setUp()
        # self.anon_user = AnonymousUser()
        # self.request_factory = RequestFactory()
        # self.view = VisualCanvasView()
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
        super_user = SuperUserFactory()
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.canvas.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_canvas'].title,
                         self.canvas.title)

    def test_user_assigned_new_cell(self):
        """Test that cannot view canvases by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.canvas.get_absolute_url(), follow=True)
        self.assertEqual(user.visual_cells.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(
            user.visual_cells.first().get_absolute_url() + 'edit/', 302)])

    def test_canvas_creator_view(self):
        """Canvas creators should be able to view their canvas."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        self.canvas.creator = user
        self.canvas.save()
        response = self.client.get(self.canvas.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_canvas'].title,
                         self.canvas.title)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = UserFactory()
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
        super_user = SuperUserFactory()
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell'].coordinates,
                         self.cell.coordinates)

    def test_user_cell_artist_edit_redirect(self):
        """Test that cannot view celles by default."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        cell = self.canvas.get_or_assign_cell(user)
        response = self.client.get(cell.get_absolute_url(), follow=True)
        self.assertEqual(user.visual_cells.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(
            user.visual_cells.first().get_absolute_url() + 'edit/', 302)])

    def test_different_artist_redirected_to_new_assigned_cell(self):
        """Test that cannot view celles by default."""
        user1 = UserFactory()
        user2 = UserFactory()
        cell1 = self.canvas.get_or_assign_cell(user1)
        login = self.client.login(username=user2.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(cell1.get_absolute_url(), follow=True)
        self.assertEqual(user2.visual_cells.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(
            user2.visual_cells.first().get_absolute_url() + 'edit/', 302)])

    def test_alread_assigned_user_redirected_to_their_cell(self):
        """Test that cannot view celles by default."""
        user1 = UserFactory()
        user2 = UserFactory()
        cell1 = self.canvas.get_or_assign_cell(user1)
        cell2 = self.canvas.get_or_assign_cell(user2)
        login = self.client.login(username=user2.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(cell1.get_absolute_url(), follow=True)
        self.assertEqual(user2.visual_cells.count(), 1)
        self.assertEqual(user2.visual_cells.last(), cell2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(
            user2.visual_cells.first().get_absolute_url() + 'edit/', 302)])

    def test_canvas_creator_user_view(self):
        """Test canvas creator views cell and won't be forwarded to edit."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        self.canvas.creator = user
        self.canvas.save()
        response = self.client.get(self.cell.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['visual_cell'].coordinates,
                         self.cell.coordinates)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = self.cell.artist
        response = self.client.get("/cell/bad-n00m835", follow=True)
        self.assertEqual(response.status_code, 404)


class TestDynamicVisualCanvasCellEditView(TestDynamicVisualCanvasCellView):

    """Test CanvasCellView adheres to permission."""

    def setUp(self):
        """Add a shortcut for correct URL."""
        super().setUp()
        self.url = self.cell.get_absolute_url() + 'edit/'
        self.EDGE_CHANGE = [1] + 11*[0]

    def test_login_redirect(self):
        """Anonymous users are redirected to login."""
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.redirect_chain[0],
                         ('/accounts/login/?next=' + self.url, 302))
        self.assertEqual(response.status_code, 200)

    def test_super_user_privilege(self):
        """Test super_users can view cells by default."""
        super_user = SuperUserFactory()
        login = self.client.login(username=super_user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['edges_vertical'],
                         [0]*12)
        response = self.client.post(self.url,
                                    {'edges_horizontal': self.EDGE_CHANGE})
        latest_edit = self.cell.latest_valid_edit
        self.assertEqual(latest_edit.edges_horizontal, self.EDGE_CHANGE)
        self.assertEqual(response.url, self.url + 'success/')
        # self.assertNotEqual(first, second))
        # self.assertEqual(response.context['visual_cell_edit'].artist,
        #                  super_user)
        # response.context['visual_cell_edit'].edges_horizontal, [0]*12
        # Need to test assigning new users/ possibly at canvas/assign/

    def test_user_cell_artist_edit(self):
        """Test that cannot view celles by default."""
        user = UserFactory()
        self.cell.artist = user
        self.cell.save()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        response = self.client.get(self.cell.get_absolute_url(), follow=True)
        self.assertEqual(response.redirect_chain[0], (self.url, 302))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['edges_vertical'],
                         [0]*12)
        response = self.client.post(self.url,
                                    {'edges_horizontal': self.EDGE_CHANGE})
        latest_edit = self.cell.latest_valid_edit
        self.assertEqual(latest_edit.edges_horizontal, self.EDGE_CHANGE)
        self.assertEqual(response.url, self.url + 'success/')

    def test_user_redirect_to_new_cell(self):
        """Test an being redirected to their own cell if they don't own it."""
        user = UserFactory()
        login = self.client.login(username=user.username,
                                  password=TEST_USER_PASSWORD)
        self.assertTrue(login)
        self.assertEqual(self.canvas.visual_cells.count(), 1)
        response = self.client.get(self.url)
        self.assertEqual(response.context['form'].initial['edges_vertical'],
                         [0]*12)
        self.assertEqual(self.canvas.visual_cells.count(), 2)

        assert False

    #  def test_standard_user_privileges(self):
    #      """Test that cannot view celles by default."""
    #      user = UserFactory()
    #      login = self.client.login(username=user.username,
    #                                password=TEST_USER_PASSWORD)
    #      self.assertTrue(login)
    #      response = self.client.get(self.url)
    #      self.assertEqual(response.status_code, 403)
    #      self.cell_edit.cell.artist = user
    #      self.cell_edit.artist = user
    #      self.cell_edit.cell.save()
    #      response = self.client.get(self.url)
    #      self.assertEqual(response.status_code, 403)

    def test_invalid_url(self):
        """Test redirect of invalid id."""
        self.client.user = UserFactory()
        response = self.client.get(self.url + '3', follow=True)
        self.assertEqual(response.status_code, 404)


class TestDynamicVisualCanvasCellEditValidView(BaseDynamicCanvasTest):

    """Test CanvasCellView manages to show cells adhering to permission."""

    def setUp(self):
        """Add a single cell on top of canvas to test view."""
        super().setUp()
        self.cell_edit = CellEditFactory(cell=CellFactory(canvas=self.canvas))
        self.url = reverse('visual:cell-valid-edit',
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
        super_user = SuperUserFactory()
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
        self.client.user = UserFactory()
        response = self.client.get(self.url + '3', follow=True)
        self.assertEqual(response.status_code, 404)


# class TestDynamicVisualCanvasCellEditHistoryView(BaseDynamicCanvasTest):
#
#     """Test CanvasCellView manages to show cells adhering to permission."""
#
#     def setUp(self):
#         """Add a single cell on top of canvas to test view."""
#         super().setUp()
#         self.cell_edit1 = CellEditFactory(cell=CellFactory(canvas=self.canvas))
#         self.cell_edit2 = CellEditFactory(cell=CellFactory(canvas=self.canvas),
#                                           is_valid=False)
#         self.cell_edit3 = CellEditFactory(cell=CellFactory(canvas=self.canvas))
#         self.urls = [reverse('visual:cell-history',
#                              kwargs={'cell_id': self.cell_edit.cell.id,
#                                      'edit_number': self.cell_edit2.edit_number})
#                      for
#
#     def test_login_redirect(self):
#         """Anonymous users are redirected to login."""
#         response = self.client.get(self.url, follow=True)
#         self.assertEqual(response.redirect_chain[0],
#                          ('/accounts/login/?next=' + self.url, 302))
#         self.assertEqual(response.status_code, 200)
#
#     def test_super_user_privilege(self):
#         """Test super_users can view cells by default."""
#         super_user = SuperUserFactory()
#         login = self.client.login(username=super_user.username,
#                                   password=TEST_USER_PASSWORD)
#         self.assertTrue(login)
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['visual_cell_edit'].edges_horizontal,
#                          [0]*12)
#
#     def test_standard_user_privileges(self):
#         """Test that cannot view celles by default."""
#         user = UserFactory()
#         login = self.client.login(username=user.username,
#                                   password=TEST_USER_PASSWORD)
#         self.assertTrue(login)
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)
#         self.cell_edit.cell.artist = user
#         self.cell_edit.artist = user
#         self.cell_edit.cell.save()
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 403)
#
#     def test_invalid_url(self):
#         """Test redirect of invalid id."""
#         self.client.user = UserFactory()
#         response = self.client.get(self.url + '3', follow=True)
#         self.assertEqual(response.status_code, 404)
