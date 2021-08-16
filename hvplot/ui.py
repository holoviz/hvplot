import numpy as np
import panel as pn
import param

from holoviews.core.util import max_range
from holoviews.plotting.util import list_cmaps
from panel.viewable import Viewer

from .converter import HoloViewsConverter as hvConverter
from .util import is_geodataframe, is_xarray

# Defaults
DATAFRAME_KINDS = sorted(set(hvConverter._kind_mapping) - set(hvConverter._gridded_types))
GRIDDED_KINDS = sorted(hvConverter._kind_mapping)
GEOM_KINDS = ['paths', 'polygons', 'points']
STATS_KINDS = ['hist', 'kde', 'boxwhisker', 'violin', 'heatmap', 'bar', 'barh']
TWOD_KINDS = ['bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'] + GEOM_KINDS
CMAPS = [cm for cm in list_cmaps() if not cm.endswith('_r_r')]
DEFAULT_CMAPS = hvConverter._default_cmaps
GEO_FEATURES = [
    'borders', 'coastline', 'land', 'lakes', 'ocean', 'rivers',
    'states', 'grid'
]
MAX_ROWS = 10_000


class Controls(Viewer):

    explorer = param.ClassSelector(class_=Viewer, precedence=-1)

    __abstract = True

    def __init__(self, df, **params):
        self._data = df
        super().__init__(**params)
        widget_kwargs = {}
        for p in self.param:
            if isinstance(self.param[p], (param.Number, param.Range)):
                widget_kwargs[p] = {'throttled': True}
        self._controls = pn.Param(
            self.param,
            max_width=300,
            show_name=False,
            sizing_mode='stretch_width',
            widgets=widget_kwargs,
        )

    def __panel__(self):
        return self._controls

    @property
    def kwargs(self):
        return {k: v for k, v in self.param.get_param_values()
                if k not in ('name', 'explorer') and v is not None and v != ''}


class Colormapping(Controls):

    clim = param.Range()

    cnorm = param.Selector(default='linear', objects=['linear', 'log', 'eq_hist'])

    color = param.String(default=None)

    colorbar = param.Boolean(default=None)

    cmap = param.Selector(default=DEFAULT_CMAPS['linear'],
                          label='Colormap', objects=CMAPS)

    symmetric = param.Boolean(default=False)

    def __init__(self, data, **params):
        super().__init__(data, **params)
        if not 'symmetric' in params:
            self.symmetric = self.explorer._converter._plot_opts.get('symmetric', False)

    @property
    def colormapped(self):
        if self.explorer.kind in hvConverter._colorbar_types:
            return True
        return self.color is not None and self.color in self._data

    @param.depends('color', 'explorer.kind', 'symmetric', watch=True)
    def _update_coloropts(self):
        if not self.colormapped or self.cmap not in list(DEFAULT_CMAPS.values()):
            return
        if self.explorer.kind in hvConverter._colorbar_types:
            key = 'diverging' if self.symmetric else 'linear'
            self.colorbar = True
        elif self.color in self._data:
            kind = self._data[self.color].dtype.kind
            if kind in 'OSU':
                key = 'categorical'
            elif self.symmetric:
                key = 'diverging'
            else:
                key = 'linear'
        else:
            return
        self.cmap = DEFAULT_CMAPS[key]


class Style(Controls):
    
    alpha = param.Magnitude(default=1)

    marker = param.Selector()


class Axes(Controls):

    legend = param.Selector(default='right', objects=hvConverter._legend_positions)

    logx = param.Boolean(default=False)

    logy = param.Boolean(default=False)

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    responsive = param.Boolean(default=False)

    shared_axes = param.Boolean(default=True)

    xlim = param.Range()

    ylim = param.Range()

    def __init__(self, data, **params):
        super().__init__(data, **params)
        self._update_ranges()

    @param.depends('explorer.xlim', 'explorer.ylim',  watch=True)
    def _update_ranges(self):
        xlim = self.explorer.xlim()
        if xlim is not None:
            self.param.xlim.bounds = xlim
        ylim = self.explorer.ylim()
        if ylim is not None:
            self.param.ylim.bounds = ylim


class Labels(Controls):

    rot = param.Integer(default=0, bounds=(0, 360))

    title = param.String()

    xlabel = param.String()

    ylabel = param.String()

class Geo(Controls):

    features = param.ListSelector(default=[], objects=GEO_FEATURES)

    geo = param.Boolean(default=False)

    project = param.Boolean(default=False)
    
    tiles = param.Selector()


class Operations(Controls):

    aggregator = param.Selector(default=None, objects=[None, 'count', 'min', 'max', 'mean', 'sum', 'any'])

    datashade = param.Boolean(default=False)

    dynspread = param.Boolean(default=False)

    rasterize = param.Boolean(default=False)

    @param.depends('datashade', watch=True)
    def _toggle_rasterize(self):
        if self.datashade:
            self.rasterize = False

    @param.depends('rasterize', watch=True)
    def _toggle_datashade(self):
        if self.rasterize:
            self.datashade = False


class hvPlotExplorer(Viewer):

    kind = param.Selector()

    x = param.Selector()

    y = param.Selector()

    y_multi = param.ListSelector(default=[], label='y')

    by = param.ListSelector(default=[])

    groupby = param.ListSelector(default=[])

    axes = param.ClassSelector(class_=Axes)

    colormapping = param.ClassSelector(class_=Colormapping)

    labels = param.ClassSelector(class_=Labels)

    geo = param.ClassSelector(class_=Geo)

    operations = param.ClassSelector(class_=Operations)

    style = param.ClassSelector(class_=Style)

    def __new__(cls, data, **params):
        if is_geodataframe(data):
            cls = hvGeomExplorer
        elif is_xarray(data):
            cls = hvGridExplorer
        else:
            cls = hvDataFrameExplorer
        return cls(data, **params)

    def __panel__(self):
        return self._layout
    
    def __init__(self, df, **params):
        x, y = params.get('x'), params.get('y')
        if 'y' in params:
            params['y_multi'] = params.pop('y') if isinstance(params['y'], list) else [params['y']]
        converter = hvConverter(df, x, y, **{k: v for k, v in params.items() if k not in ('x', 'y')})
        controller_params = {}
        for cls in param.concrete_descendents(Controls).values():
            controller_params[cls] = {
                k: params.pop(k) for k, v in dict(params).items()
                if k in cls.param
            }
        super().__init__(**params)
        self._data = df
        self._converter = converter
        self._controls = pn.Param(
            self.param, parameters=['kind', 'x', 'y', 'by', 'groupby'],
            sizing_mode='stretch_width', max_width=300
        )
        self._hv_pane = pn.pane.HoloViews(sizing_mode='stretch_width')
        self.param.watch(self._toggle_controls, 'kind')
        self.param.watch(self._check_y, 'y_multi')
        self.param.watch(self._check_by, 'by')
        self._populate()
        self._tabs = pn.Tabs(
            tabs_location='left',
            sizing_mode='stretch_width'
        )
        self.param.trigger('kind')
        controllers = {
            cls.name.lower(): cls(df, explorer=self, **params)
            for cls, params in controller_params.items()
        }
        self.param.set_param(**controllers)
        self.param.watch(self._plot, list(self.param))
        for controller in controllers.values():
            controller.param.watch(self._plot, list(controller.param))
        self._plot()
        self._layout = pn.Row(
            self._tabs,
            self._hv_pane.layout,
            sizing_mode='stretch_width'
        )
        self.param.trigger('kind')

    def _populate(self):
        variables = self._converter.variables
        for pname in self.param:
            if pname == 'kind':
                continue
            p = self.param[pname]
            if isinstance(p, param.Selector):
                p.objects = variables
    
    def _plot(self, *events):
        y = self.y_multi if 'y_multi' in self._controls.parameters else self.y
        if isinstance(y, list) and len(y) == 1:
            y = y[0]
        kwargs = {}
        for p, v in self.param.get_param_values():
            if isinstance(v, Controls):
                kwargs.update(v.kwargs)
        kwargs['min_height'] = 300
        df = self._data
        if len(df) > MAX_ROWS and not (self.kind in STATS_KINDS or kwargs.get('rasterize') or kwargs.get('datashade')):
            df = df.sample(n=MAX_ROWS)
        self._hv_pane.object = df.hvplot(
            kind=self.kind, x=self.x, y=y, by=self.by, groupby=self.groupby, **kwargs
        )

    @property
    def _single_y(self):
        if self.kind in ['labels', 'hexbin', 'heatmap', 'bivariate'] + GRIDDED_KINDS:
            return True
        return False

    def _toggle_controls(self, event):
        # Control high-level parameters
        visible = True
        if event.new in ('table', 'dataset'):
            parameters = ['kind', 'columns']
            visible = False
        elif event.new in TWOD_KINDS:
            parameters = ['kind', 'x', 'y', 'by', 'groupby']
        elif event.new in ('hist', 'kde', 'density'):
            self.x = None
            parameters = ['kind', 'y_multi', 'by', 'groupby']
        else:
            parameters = ['kind', 'x', 'y_multi', 'by', 'groupby']
        self._controls.parameters = parameters

        # Control other tabs
        tabs = [('Fields', self._controls)]
        if visible:
            tabs += [
                ('Axes', self.axes),
                ('Labels', self.labels),
                ('Style', self.style),
                ('Operations', self.operations),
                ('Geo', self.geo)
            ]
            if event.new not in ('area', 'kde', 'line', 'ohlc', 'rgb', 'step'):
                tabs.insert(5, ('Colormapping', self.colormapping))
        self._tabs[:] = tabs

    def _check_y(self, event):
        if len(event.new) > 1 and self.by:
            self.y = event.old

    def _check_by(self, event):
        if event.new and 'y_multi' in self._controls.parameters and self.y_multi and len(self.y_multi) > 1:
            self.by = []


class hvGeomExplorer(hvPlotExplorer):

    kind = param.Selector(default=None, objects=sorted(GEOM_KINDS))

    def __new__(cls, data, **params):
        return super(hvPlotExplorer, cls).__new__(cls)

    @property
    def _single_y(self):
        return True

    @property
    def _x(self):
        return None
    
    @property
    def _y(self):
        return None

    
    @param.depends('x')
    def xlim(self):
        pass
    
    @param.depends('y')
    def ylim(self):
        pass


class hvGridExplorer(hvPlotExplorer):

    kind = param.Selector(default=None, objects=sorted(GRIDDED_KINDS))

    def __new__(cls, data, **params):
        return super(hvPlotExplorer, cls).__new__(cls)
            

class hvDataFrameExplorer(hvPlotExplorer):

    z = param.Selector()

    kind = param.Selector(default='line', objects=sorted(DATAFRAME_KINDS))

    def __new__(cls, data, **params):
        return super(hvPlotExplorer, cls).__new__(cls)

    @property
    def xcat(self):
        if self.kind in ('bar', 'box', 'violin'):
            return False
        values = self._data[self.x]
        return values.dtype.kind in 'OSU'

    @property
    def _x(self):
        return (self._converter.x or self._converter.variables[0]) if self.x is None else self.x

    @property
    def _y(self):
        if 'y_multi' in self._controls.parameters and self.y_multi:
            y = self.y_multi
        elif 'y_multi' not in self._controls.parameters and self.y:
            y = self.y
        else:
            y = self._converter._process_chart_y(self._data, self._x, None, self._single_y)
        if isinstance(y, list) and len(y) == 1:
            y = y[0]
        return y

    @param.depends('x')
    def xlim(self):
        if self._x == 'index':
            values = self._data.index.values
        else:
            values = self._data[self._x]
        if values.dtype.kind in 'OSU':
            return None
        return (np.nanmin(values), np.nanmax(values))

    @param.depends('y', 'y_multi')
    def ylim(self):
        y = self._y
        if not isinstance(y, list):
            y = [y]
        values = (self._data[y] for y in y)
        return max_range([(np.nanmin(vs), np.nanmax(vs)) for vs in values])
