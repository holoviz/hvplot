import hvplot

EXPECTED_PUBLIC_API = [
    'HoloViewsConverter',
    'Interactive',
    '__version__',
    'andrews_curves',
    'bind',
    'explorer',
    'extension',
    'help',
    'hvPlot',
    'hvPlotTabular',
    'hvplot_extension',
    'lag_plot',
    'output',
    'parallel_coordinates',
    'plot',
    'post_patch',
    'render',
    'sampledata',
    'save',
    'scatter_matrix',
    'show',
]


def test_public_api():
    assert hvplot.__all__ == EXPECTED_PUBLIC_API
    assert all(hasattr(hvplot, name) for name in hvplot.__all__)
