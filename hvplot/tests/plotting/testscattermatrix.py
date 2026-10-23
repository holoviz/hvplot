import sys

import numpy as np
import pandas as pd
import pytest
from holoviews.core import GridMatrix, NdOverlay
from holoviews.element import (
    Bivariate,
    Distribution,
    HexTiles,
    Histogram,
    Scatter,
)

from hvplot import scatter_matrix


class TestScatterMatrix:
    def setup_method(self):
        self.df = pd.DataFrame(np.random.randn(1000, 4), columns=['a', 'b', 'c', 'd'])

    def test_returns_gridmatrix(self):
        sm = scatter_matrix(self.df)
        assert isinstance(sm, GridMatrix)

    def test_wrong_diagonal(self):
        with pytest.raises(ValueError):
            scatter_matrix(self.df, diagonal='wrong')

    def test_wrong_chart(self):
        with pytest.raises(ValueError):
            scatter_matrix(self.df, chart='wrong')

    def test_diagonal_default(self):
        sm = scatter_matrix(self.df)
        assert isinstance(sm['a', 'a'], Histogram)

    def test_offdiagonal_default(self):
        sm = scatter_matrix(self.df)
        assert isinstance(sm['a', 'b'], Scatter)

    def test_diagonal_kde(self):
        sm = scatter_matrix(self.df, diagonal='kde')
        assert isinstance(sm['a', 'a'], Distribution)

    def test_offdiagonal_bivariate(self):
        sm = scatter_matrix(self.df, chart='bivariate')
        assert isinstance(sm['a', 'b'], Bivariate)

    def test_offdiagonal_hexbin(self):
        sm = scatter_matrix(self.df, chart='hexbin')
        assert isinstance(sm['a', 'b'], HexTiles)

    def test_diagonal_kwargs_mutually_exclusive(self):
        with pytest.raises(TypeError):
            scatter_matrix(self.df, diagonal_kwds={'a': 1}, hist_kwds={'a': 1})
        with pytest.raises(TypeError):
            scatter_matrix(self.df, diagonal_kwds={'a': 1}, density_kwds={'a': 1})
        with pytest.raises(TypeError):
            scatter_matrix(self.df, density_kwds={'a': 1}, hist_kwds={'a': 1})

    def test_diagonal_kwargs(self):
        sm = scatter_matrix(self.df, diagonal_kwds={'line_color': 'red'})
        assert sm['a', 'a'].opts.get().kwargs['line_color'] == 'red'

    def test_c(self):
        df = self.df.copy(deep=True)
        df['e'] = np.random.choice(list('xyz'), size=len(df))
        sm = scatter_matrix(df, c='e')

        assert isinstance(sm['a', 'a'], NdOverlay)
        diag_kdims = sm['a', 'a'].kdims
        assert len(diag_kdims) == 1
        assert diag_kdims[0].name == 'e'

        assert isinstance(sm['a', 'b'], Scatter)
        offdiag_vdims = sm['a', 'b'].vdims
        assert 'e' in (d.name for d in offdiag_vdims)


class TestDatashader:
    def setup_method(self):
        try:
            import datashader  # noqa: F401
        except ImportError:
            pytest.skip('Datashader not available')
        if sys.maxsize < 2**32:
            pytest.skip('Datashader does not support 32-bit systems')
        self.df = pd.DataFrame(np.random.randn(1000, 3), columns=['a', 'b', 'c'])

    def test_rasterize_datashade_mutually_exclusive(self):
        with pytest.raises(ValueError):
            scatter_matrix(self.df, rasterize=True, datashade=True)

    def test_spread_but_no_rasterize_or_datashade(self):
        with pytest.raises(ValueError):
            scatter_matrix(self.df, dynspread=True)
        with pytest.raises(ValueError):
            scatter_matrix(self.df, spread=True)
        with pytest.raises(ValueError):
            scatter_matrix(self.df, dynspread=True, spread=True)

    @pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
    def test_rasterization(self, operation):
        sm = scatter_matrix(self.df, **{operation: True})
        dm = sm['a', 'b']
        assert dm.callback.operation.name == operation
        dm[()]
        assert len(dm.last.pipeline.operations) == 3

    @pytest.mark.parametrize('operation', ['rasterize', 'datashade'])
    def test_datashade_aggregator(self, operation):
        sm = scatter_matrix(self.df, aggregator='mean', **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert dm.last.pipeline.operations[-1].aggregator == 'mean'

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_rasterize(self, operation):
        sm = scatter_matrix(self.df, rasterize=True, **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert len(dm.last.pipeline.operations) == 4

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_datashade(self, operation):
        sm = scatter_matrix(self.df, datashade=True, **{operation: True})
        dm = sm['a', 'b']
        dm[()]
        assert len(dm.last.pipeline.operations) == 4

    @pytest.mark.parametrize('operation', ['spread', 'dynspread'])
    def test_spread_kwargs(self, operation):
        sm = scatter_matrix(self.df, datashade=True, **{operation: True, 'shape': 'circle'})
        dm = sm['a', 'b']
        dm[()]
        assert dm.last.pipeline.operations[-1].args[0].keywords['shape'] == 'circle'
