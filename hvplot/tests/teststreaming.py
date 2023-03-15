from unittest import TestCase

import pandas as pd

from holoviews.streams import Buffer, Pipe


class TestExplicitStreamPlotting(TestCase):

    def setUp(self):
        import hvplot.pandas   # noqa
        self.df = pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])

    def test_pipe_stream(self):
        stream = Pipe(data=self.df)
        plot = self.df.hvplot('x', 'y', stream=stream)
        pd.testing.assert_frame_equal(plot[()].data, self.df)
        new_df = pd.DataFrame([[7, 8], [9, 10]], columns=['x', 'y'])
        stream.send(new_df)
        pd.testing.assert_frame_equal(plot[()].data, new_df)

    def test_buffer_stream(self):
        stream = Buffer(data=self.df, index=False)
        plot = self.df.hvplot('x', 'y', stream=stream)
        pd.testing.assert_frame_equal(plot[()].data, self.df)
        new_df = pd.DataFrame([[7, 8], [9, 10]], columns=['x', 'y'])
        stream.send(new_df)
        pd.testing.assert_frame_equal(plot[()].data, pd.concat([self.df, new_df]))
