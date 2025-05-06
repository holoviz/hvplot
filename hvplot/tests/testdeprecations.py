"""
Tests for deprecation warnings.
"""

import pandas as pd
import pytest

from hvplot.converter import HoloViewsConverter


def test_converter_argument_debug(disable_param_warnings_as_exceptions):
    df = pd.DataFrame({'x': [0, 1], 'y': [0, 1]})
    with pytest.warns(DeprecationWarning):
        HoloViewsConverter(df, 'x', 'y', debug=True)
