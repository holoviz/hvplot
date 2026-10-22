import sys

import pandas as pd
import pytest
from holoviews import Store
from holoviews.core import GridMatrix, NdOverlay
from holoviews.element import (
    Bivariate,
    Distribution,
    HexTiles,
    Histogram,
    Scatter,
)

from hvplot import scatter_matrix
from hvplot.tests._deps import requires


@pytest.fixture
def df(rng):
    return pd.DataFrame(rng.standard_normal((1000, 4)), columns=['a', 'b', 'c', 'd'])


def test_returns_gridmatrix(df):
    sm = scatter_matrix(df)
    assert isinstance(sm, GridMatrix)


def test_wrong_diagonal(df):
    with pytest.raises(ValueError):
        scatter_matrix(df, diagonal='wrong')


def test_wrong_chart(df):
    with pytest.raises(ValueError):
        scatter_matrix(df, chart='wrong')


def test_diagonal_default(df):
    sm = scatter_matrix(df)
    assert isinstance(sm['a', 'a'], Histogram)


def test_offdiagonal_default(df):
    sm = scatter_matrix(df)
    assert isinstance(sm['a', 'b'], Scatter)


def test_diagonal_kde(df):
    sm = scatter_matrix(df, diagonal='kde')
    assert isinstance(sm['a', 'a'], Distribution)


def test_offdiagonal_bivariate(df):
    sm = scatter_matrix(df, chart='bivariate')
    assert isinstance(sm['a', 'b'], Bivariate)


def test_offdiagonal_hexbin(df):
    sm = scatter_matrix(df, chart='hexbin')
    assert isinstance(sm['a', 'b'], HexTiles)


@pytest.mark.parametrize(
    'kwargs',
    [
        {'diagonal_kwds': {'a': 1}, 'hist_kwds': {'a': 1}},
        {'diagonal_kwds': {'a': 1}, 'density_kwds': {'a': 1}},
        {'density_kwds': {'a': 1}, 'hist_kwds': {'a': 1}},
    ],
)
def test_diagonal_kwargs_mutually_exclusive(df, kwargs):
    with pytest.raises(TypeError):
        scatter_matrix(df, **kwargs)


def test_diagonal_kwargs(df):
    sm = scatter_matrix(df, diagonal_kwds={'line_color': 'red'})
    opts = Store.lookup_options('bokeh', sm['a', 'a'], 'style')
    assert opts.kwargs['line_color'] == 'red'


def test_c(df, rng):
    df['e'] = rng.choice(list('xyz'), size=len(df))
    sm = scatter_matrix(df, c='e')

    assert isinstance(sm['a', 'a'], NdOverlay)
    diag_kdims = sm['a', 'a'].kdims
    assert len(diag_kdims) == 1
    assert diag_kdims[0].name == 'e'

    assert isinstance(sm['a', 'b'], Scatter)
    offdiag_vdims = sm['a', 'b'].vdims
    assert 'e' in (d.name for d in offdiag_vdims)


@requires('datashader')
@pytest.mark.skipif(sys.maxsize < 2**32, reason='Datashader does not support 32-bit systems')
class TestDatashader:
    def test_rasterize_datashade_mutually_exclusive(self, df):
        with pytest.raises(ValueError):
            scatter_matrix(df, rasterize=True, datashade=True)

    @pytest.mark.parametrize(
        'kwargs', [{'dynspread': True}, {'spread': True}, {'dynspread': True, 'spread': True}]
    )
    def test_spread_but_no_rasterize_or_datashade(self, df, kwargs):
        with pytest.raises(ValueError):
            scatter_matrix(df, **kwargs)

    @pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
    def test_rasterization(self, df, operation):
        sm = scatter_matrix(df, **{operation: True})
        dm = sm['a', 'b']
        assert dm.callback.operation.name == operation
        dm[()]
        assert len(dm.last.pipeline.operations) == 3

    @pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
    def test_datashade_aggregator(self, df, operation):
        sm = scatter_matrix(df, aggregator='mean', **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert dm.last.pipeline.operations[-1].aggregator == 'mean'

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_rasterize(self, df, operation):
        sm = scatter_matrix(df, rasterize=True, **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert len(dm.last.pipeline.operations) == 4

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_datashade(self, df, operation):
        sm = scatter_matrix(df, datashade=True, **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert len(dm.last.pipeline.operations) == 4

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_kwargs(self, df, operation):
        sm = scatter_matrix(df, datashade=True, **{operation: True, 'shape': 'circle'})
        dm = sm['a', 'b']
        dm[()]
        assert dm.last.pipeline.operations[-1].args[0].keywords['shape'] == 'circle'
