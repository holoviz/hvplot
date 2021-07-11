
import panel as pn
import param

from holoviews.plotting.util import list_cmaps
from panel.viewable import Viewer

from .converter import HoloViewsConverter as hvConverter


kinds = set(hvConverter._kind_mapping) - set(hvConverter._gridded_types)
COLORMAPS = [cm for cm in list_cmaps() if not cm.endswith('_r_r')]
MAX_ROWS = 10_000


class Controls(Viewer):

    def __init__(self, df, **params):
        super().__init__(**params)
        self._controls = pn.Param(
            self.param, show_name=False, sizing_mode='stretch_width', max_width=300)

    def __panel__(self):
        return self._controls

    @property
    def kwargs(self):
        return {k: v for k, v in self.param.get_param_values()
                if k != 'name' and v}


class Style(Controls):

    cnorm = param.Selector(default='linear', objects=['linear', 'log', 'eq_hist'])

    color = param.String(default=None)

    cmap = param.Selector(default=None, label='Colormap', objects=COLORMAPS)

    alpha = param.Magnitude(default=1)


class Axes(Controls):

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    shared_axes = param.Boolean(default=True)

    responsive = param.Boolean(default=False)


class Labels(Controls):

    title = param.String()

    xlabel = param.String()

    ylabel = param.String()


class Operations(Controls):

    datashade = param.Boolean(default=False)

    rasterize = param.Boolean(default=False)

    dynspread = param.Boolean(default=False)

    aggregator = param.Selector(default=None, objects=[None, 'count', 'min', 'max', 'mean', 'sum'])

    @param.depends('datashade', watch=True)
    def _toggle_rasterize(self):
        if self.datashade:
            self.rasterize = False

    @param.depends('rasterize', watch=True)
    def _toggle_datashade(self):
        if self.rasterize:
            self.datashade = False


class hvPlotExplorer(Viewer):

    kind = param.Selector(default='line', objects=sorted(kinds))

    x = param.Selector()

    y = param.Selector()

    y_multi = param.ListSelector(default=[], label='y')

    by = param.ListSelector(default=[])

    groupby = param.ListSelector(default=[])

    style = param.ClassSelector(class_=Style)

    axes = param.ClassSelector(class_=Axes)

    labels = param.ClassSelector(class_=Labels)

    operations = param.ClassSelector(class_=Operations)

    def __init__(self, df, **params):
        if 'y' in params:
            params['y_multi'] = params.pop('y') if isinstance(params['y'], list) else [params['y']]
        params['style'] = Style(df, **{k: params.pop(k) for k, v in dict(params).items() if k in Style.param})
        params['axes'] = Axes(df, **{k: params.pop(k) for k, v in dict(params).items() if k in Axes.param})
        params['labels'] = Labels(df, **{k: params.pop(k) for k, v in dict(params).items() if k in Labels.param})
        params['operations'] = Operations(df, **{k: params.pop(k) for k, v in dict(params).items() if k in Operations.param})
        super().__init__(**params)
        self._df = df
        self._controls = pn.Param(
            self.param, parameters=['kind', 'x', 'y', 'by', 'groupby'],
            sizing_mode='stretch_width', max_width=300
        )
        self._hv_pane = pn.pane.HoloViews(sizing_mode='stretch_width')
        self.param.watch(self._disable, 'kind')
        self.param.watch(self._check_y, 'y_multi')
        self.param.watch(self._check_by, 'by')
        self.param.watch(self._plot, list(self.param))
        self.axes.param.watch(self._plot, list(self.axes.param))
        self.style.param.watch(self._plot, list(self.style.param))
        self.labels.param.watch(self._plot, list(self.labels.param))
        self.operations.param.watch(self._plot, list(self.operations.param))
        self._populate()
        self.param.trigger('kind')

    def _populate(self):
        index = self._df.index.names
        columns = list(self._df.columns)
        if index == [None]:
            columns.insert(0, 'index')
        else:
            columns = list(index) + columns
        for pname in self.param:
            if pname == 'kind':
                continue
            p = self.param[pname]
            if isinstance(p, param.Selector):
                p.objects = columns

    def _disable(self, event):
        if event.new in ('hist', 'kde'):
            self.x = None
            self.param.x.precedence = -1
        else:
            self.param.x.precedence = None
        if event.new in ('bivariate', 'heatmap', 'hexbin', 'labels', 'paths', 'polygons', 'vectorfield'):
            self._controls.parameters = ['kind', 'x', 'y', 'by', 'groupby']
        else:
            self._controls.parameters = ['kind', 'x', 'y_multi', 'by', 'groupby']
        precedence = -1 if event.new == 'table' else 0
        for p in ('x', 'y', 'y_multi', 'by', 'groupby', 'color', 'alpha'):
            self.param.precedence = precedence

    def _check_y(self, event):
        if len(event.new) > 1 and self.by:
            self.y = event.old

    def _check_by(self, event):
        if event.new and 'y_multi' in self._controls.parameters and self.y_multi and len(self.y_multi) > 1:
            self.by = []

    def _plot(self, *events):
        y = self.y_multi if 'y_multi' in self._controls.parameters else self.y
        kwargs = dict(self.axes.kwargs, **self.style.kwargs)
        kwargs.update(self.labels.kwargs)
        kwargs.update(self.operations.kwargs)
        kwargs['min_height'] = 300
        df = self._df
        if len(df) > MAX_ROWS and not (self.kind in ('hist', 'kde', 'boxwhisker', 'violin') or kwargs.get('rasterize') or kwargs.get('datashade')):
            df = df.sample(n=MAX_ROWS)
        self._hv_pane.object = df.hvplot(
            kind=self.kind, x=self.x, y=y, by=self.by, groupby=self.groupby, **kwargs
        )

    def __panel__(self):
        return pn.Row(
            pn.Tabs(
                ('Fields', self._controls),
                ('Style', self.style),
                ('Plot', self.axes),
                ('Labels', self.labels),
                ('Operations', self.operations),
                tabs_location='left',
                sizing_mode='stretch_width'
            ),
            self._hv_pane.layout,
            sizing_mode='stretch_width'
        )
