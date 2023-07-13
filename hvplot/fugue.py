from typing import Any, Dict, Tuple

import panel as _pn
import hvplot.pandas  # noqa: F401
from fugue import DataFrames, Outputter
from fugue.extensions import namespace_candidate, parse_outputter
from hvplot import hvPlotTabular, show


@parse_outputter.candidate(namespace_candidate("hvplot", lambda x: isinstance(x, str)))
def _parse_hvplot(obj: Tuple[str, str]) -> Outputter:
    return _Visualize(obj[1])


class _Visualize(Outputter):
    def __init__(self, func: str) -> None:
        super().__init__()
        self._func = func
        getattr(hvPlotTabular, func)  # ensure the func exists

    def process(self, dfs: DataFrames) -> None:
        """
        Process the dataframes and output the result as
        pn.Column or pn.pane.HoloViews.

        Parameters:
        -----------
        dfs: fugue.DataFrames
        """
        charts = []
        for df in dfs.values():
            params = dict(self.params)
            opts: Dict[str, Any] = params.pop("opts", {})
            chart = getattr(df.as_pandas().hvplot, self._func)(**params).opts(**opts)
            charts.append(chart)
        col = _pn.Column(*charts)
        try:
            from IPython.display import display
            display(col)  # in notebook
        except ImportError:
            show(col)  # in script
