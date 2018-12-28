from django.urls import reverse, resolve

from ..models import VisualCellEdit
from .test_dynamic import BaseDynamicCanvasTest
from .utils import UserFactory


class TestDynamicURLs(BaseDynamicCanvasTest):

    """Test Dynamic Canvas URL structure, including reassignment."""

    def test_canvas_url(self):
        """Test url structure for initial dynamic canvas."""
        # user = UserFactory()
        self.assertEqual(reverse('visual:canvas',
                                 kwargs={'canvas_id': self.canvas.id}),
                         f'/visual/canvas/{self.canvas.id}/')
        self.assertEqual(resolve(f'/visual/canvas/{self.canvas.id}/').view_name,
                         'visual:canvas')

    def test_cell_url(self):
        """Test url structure for initial dynamic canvas."""
        user = UserFactory()
        cell = self.canvas.get_or_create_contiguous_cell()
        cell.artist = user
        cell.save()
        self.assertEqual(reverse('visual:cell',
                                 kwargs={'canvas_id': self.canvas.id,
                                         'cell_id': user.id}),
                         f'/visual/canvas/{self.canvas.id}/{user.id}/')
        self.assertEqual(
            resolve(f'/visual/canvas/{self.canvas.id}/{user.id}/').view_name,
            'visual:cell')

    def test_cell_edit_urls(self):
        """Test URLs as cell edits get saved with default length 8."""
        user = UserFactory()
        cell = self.canvas.get_or_create_contiguous_cell()
        cell.artist = user
        cell.save()
        edit1 = VisualCellEdit(edges_horizontal=[0, 1, 0, 0, 0, 0, 0, 0],
                               edges_vertical=[0, 0, 1, 0, 0, 0, 0, 0],
                               edges_south_east=[0, 0, 0, 0, 0, 0, 0, 0],
                               edges_south_west=[0, 0, 0, 0, 0, 0, 0, 0])
        edit2 = VisualCellEdit(edges_horizontal=[0, 1, 1, 0, 0, 0, 0, 0],
                               edges_vertical=[0, 0, 1, 0, 0, 0, 0, 0],
                               edges_south_east=[0, 0, 1, 0, 0, 0, 0, 0],
                               edges_south_west=[0, 0, 0, 0, 0, 0, 0, 0])
        for i, edit in enumerate([edit1, edit2], 1):
            with self.subTest(edit=edit):
                cell.edits.add(edit, bulk=False)
                self.assertEqual(
                    reverse('visual:cell-edit',
                            kwargs={'canvas_id': self.canvas.id,
                                    'cell_id': user.id,
                                    'edit_number': i}),
                    (f'/visual/canvas/{self.canvas.id}/{user.id}/'
                     f'{edit.edit_number}/'))
                self.assertEqual(
                    resolve(f'/visual/canvas/{self.canvas.id}/'
                            f'{user.id}/{edit.edit_number}/').view_name,
                    'visual:cell-edit')
