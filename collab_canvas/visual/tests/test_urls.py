from django.urls import reverse, resolve

from ..models import VisualCellEdit
from .test_dynamic import BaseDynamicCanvasTest
from .utils import CellFactory, UserFactory


class TestDynamicURLs(BaseDynamicCanvasTest):

    """Test Dynamic Canvas URL structure, including reassignment."""

    def test_canvas_url(self):
        """Test url structure for initial dynamic canvas."""
        # user = UserFactory()
        self.assertEqual(self.canvas.get_absolute_url(),
                         f'/visual/canvas/{self.canvas.id}/')
        self.assertEqual(reverse('visual:canvas',
                                 kwargs={'canvas_id': self.canvas.id}),
                         f'/visual/canvas/{self.canvas.id}/')
        self.assertEqual(resolve(f'/visual/canvas/{self.canvas.id}/').view_name,
                         'visual:canvas')

    def test_cell_url(self):
        """Test url structure for initial dynamic canvas."""
        cell = CellFactory(canvas=self.canvas)
        self.assertEqual(cell.get_absolute_url(),
                         f'/visual/canvas/{self.canvas.id}/{cell.id}/')
        self.assertEqual(reverse('visual:cell',
                                 kwargs={'canvas_id': self.canvas.id,
                                         'cell_id': cell.artist.id}),
                         f'/visual/canvas/{self.canvas.id}/{cell.artist.id}/')
        self.assertEqual(
            resolve(f'/visual/canvas/{self.canvas.id}/{cell.artist.id}/').view_name,
            'visual:cell')

    def test_cell_edit_urls(self):
        """Test URLs as cell edits get saved with default length 8."""
        user = UserFactory()
        cell = self.canvas.get_or_create_contiguous_cell()
        cell.artist = user
        cell.save()
        # This should fill in the blank cells correctly by calling full_clean
        edit1 = VisualCellEdit(cell=cell, artist=user,
                               edges_horizontal=[0, 1] + [0]*10,
                               edges_vertical=[0]*12,
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9)
        edit2 = VisualCellEdit(cell=cell, artist=user,
                               edges_horizontal=[0, 1, 1] + [0]*9,
                               edges_vertical=[0]*12,
                               edges_south_east=[0]*9,
                               edges_south_west=[0]*9)
        for i, edit in enumerate([edit1, edit2], 1):
            with self.subTest(edit=edit):
                edit.full_clean()
                cell.edits.add(edit, bulk=False)
                self.assertEqual(edit.get_absolute_url(),
                                 f'/visual/canvas/{self.canvas.id}/'
                                 f'{cell.id}/history/{i}/')
                self.assertEqual(
                    reverse('visual:cell-edit',
                            kwargs={'canvas_id': self.canvas.id,
                                    'cell_id': cell.id,
                                    'edit_number': i}),
                    (f'/visual/canvas/{self.canvas.id}/{cell.id}/'
                     f'{edit.history_number}/'))
                self.assertEqual(
                    resolve(f'/visual/canvas/{self.canvas.id}/'
                            f'{cell.id}/{edit.history_number}/').view_name,
                    'visual:cell-edit')

    # def test_cell_history_urls(self):
    #     """Test history consistency even if some edits aren't valid."""
    #     users = [UserFactory() for i in range(2)]
    #     for u in users:
    #         cell = self.canvas.get_or_create_contiguous_cell()
    #         cell.artist = u
    #         cell.save()
        # canvases = [CanvasFactory() for c in 2]
