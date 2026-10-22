import pandas as pd
import pytest
from holoviews.streams import Buffer, Pipe

pytestmark = pytest.mark.usefixtures('hvplot_pandas')


@pytest.fixture
def df():
    return pd.DataFrame([[1, 2], [3, 4], [5, 6]], columns=['x', 'y'])


def test_stream_pipe(df):
    stream = Pipe(data=df)
    plot = df.hvplot('x', 'y', stream=stream)
    pd.testing.assert_frame_equal(plot[()].data, df)
    new_df = pd.DataFrame([[7, 8], [9, 10]], columns=['x', 'y'])
    stream.send(new_df)
    pd.testing.assert_frame_equal(plot[()].data, new_df)


def test_stream_buffer(df):
    stream = Buffer(data=df, index=False)
    plot = df.hvplot('x', 'y', stream=stream)
    pd.testing.assert_frame_equal(plot[()].data, df)
    new_df = pd.DataFrame([[7, 8], [9, 10]], columns=['x', 'y'])
    stream.send(new_df)
    pd.testing.assert_frame_equal(plot[()].data, pd.concat([df, new_df]))
