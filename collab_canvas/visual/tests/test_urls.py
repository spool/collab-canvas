from django.urls import reverse, resolve

from .test_dynamic import BaseDynamicCanvasTest
from .utils import CellEditFactory, CellFactory


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
                         f'/visual/canvas/cell/{cell.id}/')
        self.assertEqual(reverse('visual:cell',
                                 kwargs={'cell_id': cell.artist.id}),
                         f'/visual/canvas/cell/{cell.artist.id}/')
        self.assertEqual(
            resolve(f'/visual/canvas/cell/{cell.artist.id}/').view_name,
            'visual:cell')

    def test_cell_edit_url(self):
        """Test URLs as cell edits get saved with 3x3 dimensions."""
        cell_edit = CellEditFactory(cell=CellFactory(canvas=self.canvas))
        cell_edit.clean()
        self.assertEqual(cell_edit.get_absolute_url(),
                         f'/visual/canvas/cell/{cell_edit.cell.id}/history/1/')
        self.assertEqual(
            reverse('visual:cell-valid-edit',
                    kwargs={'cell_id': cell_edit.cell.id,
                            'edit_number': 1}),
            (f'/visual/canvas/cell/{cell_edit.cell.id}/'
             f'{cell_edit.history_number}/'))
        self.assertEqual(
            resolve(f'/visual/canvas/cell/{cell_edit.cell.id}/'
                    f'{cell_edit.history_number}/').view_name,
            'visual:cell-valid-edit')

    def test_cell_continuous_creation(self):
        """
        Test URLs as cell edits get saved.

        Todo:
            * Assess need to start with 1 rather than 0
            * Might be assumption of initial state is 0, but given neighbours
            may need to include that.
        """
        HORIZONTAL_EDGES = {1: [0, 1] + [0]*10,
                            2: [0, 1, 1] + [0]*9}
        # cell1 =
        cell = CellFactory(canvas=self.canvas)
        # edit1 = CellEditFactory(edges_horizontal=[0, 1] + [0]*10,
        #                         )
        # edit2 = CellEditFactory(edges_horizontal=[0, 1, 1] + [0]*9,
        #                         cell=edit1.cell,
        #                         artist=edit1.artist)
        # IDs will likely start at 1
        # https://docs.djangoproject.com/en/2.1/ref/models/options/#order-with-respect-to
        for i in range(3, 1):
            with self.subTest(f"Test cell edit {i}", i=i):
                edit = CellEditFactory(cell=cell, artist=cell.artist,
                                       edges_horizontal=HORIZONTAL_EDGES[i])
                edit.full_clean()
                # cell.edits.add(edit, bulk=False)
                self.assertEqual(edit.get_absolute_url(),
                                 f'/visual/canvas/cell/{cell.id}/history/{i}/')
                self.assertEqual(
                    reverse('visual:cell-valid-edit',
                            kwargs={'cell_id': cell.id, 'edit_number': i}),
                    (f'/visual/canvas/cell/{cell.id}/{edit.history_number}/'))
                self.assertEqual(
                    resolve('/visual/canvas/cell/'
                            f'{cell.id}/{edit.history_number}/').view_name,
                    'visual:cell-valid-edit')

    # def test_cell_history_urls(self):
    #     """Test history consistency even if some edits aren't valid."""
    #     users = [UserFactory() for i in range(2)]
    #     for u in users:
    #         cell = self.canvas.get_or_create_contiguous_cell()
    #         cell.artist = u
    #         cell.save()
        # canvases = [CanvasFactory() for c in 2]
