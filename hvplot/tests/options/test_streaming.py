import holoviews as hv
import pandas as pd
import pytest
from holoviews.streams import Buffer, Pipe

from hvplot.tests._deps import requires
from hvplot.util import _HV_VERSION

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


@requires('streamz')
@pytest.mark.skipif(
    _HV_VERSION >= (1, 23, 0), reason='streamz support has been removed in HoloViews >= 1.23.0'
)
@pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning')
def test_backlog(df):
    # backlog only applies to streamz data, streamz is optional.
    from streamz.dataframe import DataFrame as StreamingDataFrame

    import hvplot.streamz  # noqa: F401

    sdf = StreamingDataFrame(example=df)
    plot = sdf.hvplot('x', 'y', backlog=2)
    buffer = plot.streams[0]
    assert isinstance(buffer, Buffer)
    assert buffer.length == 2


def test_stream_invalid_type_error(df):
    with pytest.raises(ValueError, match='not recognized'):
        df.hvplot('x', 'y', stream=hv.streams.Stream())


def test_stream_with_groupby_error(df):
    with pytest.raises(NotImplementedError, match='Streaming and groupby'):
        df.hvplot('x', 'y', stream=Pipe(data=df), groupby='y')


@requires('streamz')
@pytest.mark.skipif(
    _HV_VERSION < (1, 23, 0), reason='streamz is only an error in HoloViews >= 1.23.0'
)
@pytest.mark.filterwarnings('ignore:streamz support has been deprecated:FutureWarning')
def test_backlog_streamz_removed_error(df):
    from streamz.dataframe import DataFrame as StreamingDataFrame

    import hvplot.streamz  # noqa: F401

    with pytest.raises(RuntimeError, match='streamz support has been deprecated'):
        StreamingDataFrame(example=df).hvplot('x', 'y', backlog=2)
