from typing import Any, Dict, Tuple

from triad import assert_or_throw

import hvplot.pandas  # type: ignore
import pandas as pd  # type: ignore
from fugue import DataFrames, Outputter  # type: ignore
from fugue.exceptions import FugueWorkflowError  # type: ignore
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
        assert_or_throw(len(dfs) == 1, FugueWorkflowError("not single input"))
        df = dfs[0].as_pandas()
        params = dict(self.params)
        opts: Dict[str, Any] = params.pop("opts", {})
        chart = getattr(df.hvplot, self._func)(**params).opts(**opts)
        try:
            from IPython.display import display
            display(chart)  # in notebook
        except ImportError:
            show(chart)  # in script
