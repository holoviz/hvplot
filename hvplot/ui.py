import holoviews as _hv
import numpy as np
import panel as pn
import param

from holoviews.core.util import is_number, max_range
from holoviews.element import tile_sources
from holoviews.plotting.util import list_cmaps
from panel.viewable import Viewer

from .converter import HoloViewsConverter as _hvConverter
from .plotting import hvPlot as _hvPlot
from .util import is_geodataframe, is_xarray

# Defaults
DATAFRAME_KINDS = sorted(set(_hvConverter._kind_mapping) - set(_hvConverter._gridded_types))
GRIDDED_KINDS = sorted(_hvConverter._kind_mapping)
GEOM_KINDS = ['paths', 'polygons', 'points']
STATS_KINDS = ['hist', 'kde', 'boxwhisker', 'violin', 'heatmap', 'bar', 'barh']
TWOD_KINDS = ['bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield'] + GEOM_KINDS
CMAPS = [cm for cm in list_cmaps() if not cm.endswith('_r_r')]
DEFAULT_CMAPS = _hvConverter._default_cmaps
GEO_FEATURES = [
    'borders', 'coastline', 'land', 'lakes', 'ocean', 'rivers',
    'states', 'grid'
]
GEO_TILES = list(tile_sources)
AGGREGATORS = [None, 'count', 'min', 'max', 'mean', 'sum', 'any']
MAX_ROWS = 10000


def explorer(data, **kwargs):
    """Explore your data by building a plot in a Panel UI component.

    This function returns a Panel component that has on the right-side
    hand a plot view and on the left-side hand a number of widgets that
    control the plot.

    Parameters
    ----------
    data : pandas.DataFrame
        Data structure to explore.

    Returns
    -------
    hvplotExporer
        Panel component to explore a dataset.
    """
    return hvPlotExplorer.from_data(data, **kwargs)


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
        return {k: v for k, v in self.param.values().items()
                if k not in ('name', 'explorer') and v is not None and v != ''}


class Colormapping(Controls):

    clim = param.Range()

    cnorm = param.Selector(default='linear', objects=['linear', 'log', 'eq_hist'])

    color = param.String(default=None)

    colorbar = param.Boolean(default=None)

    cmap = param.Selector(default=DEFAULT_CMAPS['linear'],
                          label='Colormap', objects=CMAPS)

    rescale_discrete_levels = param.Boolean(default=True)

    symmetric = param.Boolean(default=False)

    def __init__(self, data, **params):
        super().__init__(data, **params)
        if not 'symmetric' in params:
            self.symmetric = self.explorer._converter._plot_opts.get('symmetric', False)

    @property
    def colormapped(self):
        if self.explorer.kind in _hvConverter._colorbar_types:
            return True
        return self.color is not None and self.color in self._data

    @param.depends('color', 'explorer.kind', 'symmetric', watch=True)
    def _update_coloropts(self):
        if not self.colormapped or self.cmap not in list(DEFAULT_CMAPS.values()):
            return
        if self.explorer.kind in _hvConverter._colorbar_types:
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


class Axes(Controls):

    legend = param.Selector(default='right', objects=_hvConverter._legend_positions)

    logx = param.Boolean(default=False)

    logy = param.Boolean(default=False)

    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    responsive = param.Boolean(default=False)

    shared_axes = param.Boolean(default=True)

    xlim = param.Range()

    ylim = param.Range()

    logx = param.Boolean(default=False)

    logy = param.Boolean(default=False)

    def __init__(self, data, **params):
        super().__init__(data, **params)
        self._update_ranges()

    @param.depends('explorer.xlim', 'explorer.ylim',  watch=True)
    def _update_ranges(self):
        xlim = self.explorer.xlim()
        if xlim is not None and is_number(xlim[0]) and is_number(xlim[1]):
            self.param.xlim.precedence = 0
            self.param.xlim.bounds = xlim
        else:
            self.param.xlim.precedence = -1
        ylim = self.explorer.ylim()
        if ylim is not None and is_number(ylim[0]) and is_number(ylim[1]):
            self.param.ylim.precedence = 0
            self.param.ylim.bounds = ylim
        else:
            self.param.ylim.precedence = -1


class Labels(Controls):

    title = param.String(doc="Title for the plot")

    xlabel = param.String(doc="Axis labels for the x-axis.")

    ylabel = param.String(doc="Axis labels for the y-axis.")

    clabel = param.String(doc="Axis labels for the colorbar.")

    fontscale = param.Number(default=1, doc="""
        Scales the size of all fonts by the same amount, e.g. fontscale=1.5
        enlarges all fonts (title, xticks, labels etc.) by 50%.""")

    rot = param.Integer(default=0, bounds=(0, 360), doc="""
        Rotates the axis ticks along the x-axis by the specified
        number of degrees.""")


class Geo(Controls):

    geo = param.Boolean(default=False, doc="""
        Whether the plot should be treated as geographic (and assume
        PlateCarree, i.e. lat/lon coordinates).""")

    crs = param.Selector(default=None, doc="""
        Coordinate reference system of the data specified as Cartopy
        CRS object, proj.4 string or EPSG code.""")

    crs_kwargs = param.Dict(default={}, doc="""
        Keyword arguments to pass to selected CRS.""")

    global_extent = param.Boolean(default=False, doc="""
        Whether to expand the plot extent to span the whole globe.""")

    project = param.Boolean(default=False, doc="""
        Whether to project the data before plotting (adds initial
        overhead but avoids projecting data when plot is dynamically
        updated).""")

    features = param.ListSelector(default=[], objects=GEO_FEATURES, doc="""
        A list of features or a dictionary of features and the scale
        at which to render it. Available features include 'borders',
        'coastline', 'lakes', 'land', 'ocean', 'rivers' and 'states'.""")

    tiles = param.ObjectSelector(default=None, objects=GEO_TILES, doc="""
        Whether to overlay the plot on a tile source. Tiles sources
        can be selected by name or a tiles object or class can be passed,
        the default is 'Wikipedia'.""")

    @param.depends('geo', 'project', 'features', watch=True, on_init=True)
    def _update_crs(self):
        enabled = bool(self.geo or self.project or self.features)
        self.param.crs.constant = not enabled
        self.param.crs_kwargs.constant = not enabled
        self.geo = enabled
        if not enabled:
            return
        from cartopy.crs import CRS, GOOGLE_MERCATOR
        crs = {
            k: v for k, v in param.concrete_descendents(CRS).items()
            if not k.startswith('_') and k != 'CRS'
        }
        crs['WebMercator'] = GOOGLE_MERCATOR
        self.param.crs.objects = crs



class Operations(Controls):

    datashade = param.Boolean(default=False, doc="""
        Whether to apply rasterization and shading using datashader
        library returning an RGB object.""")

    rasterize = param.Boolean(default=False, doc="""
        Whether to apply rasterization using the datashader library
        returning an aggregated Image.""")

    aggregator = param.Selector(default=None, objects=AGGREGATORS, doc="""
        Aggregator to use when applying rasterize or datashade operation.""")

    dynspread = param.Boolean(default=False, doc="""
        Allows plots generated with datashade=True or rasterize=True
        to increase the point size to make sparse regions more visible.""")

    x_sampling = param.Number(default=None, doc="""
        Specifies the smallest allowed sampling interval along the x-axis.""")

    y_sampling = param.Number(default=None, doc="""
        Specifies the smallest allowed sampling interval along the y-axis.""")

    @param.depends('datashade', watch=True)
    def _toggle_rasterize(self):
        if self.datashade:
            self.rasterize = False

    @param.depends('rasterize', watch=True)
    def _toggle_datashade(self):
        if self.rasterize:
            self.datashade = False

    @param.depends('rasterize', 'datashade', watch=True, on_init=True)
    def _update_options(self):
        enabled = self.rasterize or self.datashade
        self.param.dynspread.constant = not enabled
        self.param.x_sampling.constant = not enabled
        self.param.y_sampling.constant = not enabled
        self.param.aggregator.constant = not enabled


class hvPlotExplorer(Viewer):

    kind = param.Selector()

    x = param.Selector()

    y = param.Selector()

    y_multi = param.ListSelector(default=[], label='y')

    by = param.ListSelector(default=[])

    groupby = param.ListSelector(default=[])

    # Controls that will show up as new tabs, must be ClassSelector

    axes = param.ClassSelector(class_=Axes)

    colormapping = param.ClassSelector(class_=Colormapping)

    labels = param.ClassSelector(class_=Labels)

    # Hide the geo tab until it's better supported
    # geo = param.ClassSelector(class_=Geo)

    operations = param.ClassSelector(class_=Operations)

    style = param.ClassSelector(class_=Style)

    @classmethod
    def from_data(cls, data, **params):
        if is_geodataframe(data):
            # cls = hvGeomExplorer
            raise TypeError('GeoDataFrame objects not yet supported.')
        elif is_xarray(data):
            # cls = hvGridExplorer
            raise TypeError('Xarray objects not yet supported.')
        else:
            cls = hvDataFrameExplorer
        return cls(data, **params)

    def __panel__(self):
        return self._layout

    def __init__(self, df, **params):
        x, y = params.get('x'), params.get('y')
        if 'y' in params:
            params['y_multi'] = params.pop('y') if isinstance(params['y'], list) else [params['y']]
        converter = _hvConverter(
            df, x, y,
            **{k: v for k, v in params.items() if k not in ('x', 'y', 'y_multi')}
        )
        controller_params = {}
        # Assumes the controls aren't passed on instantiation.
        controls = [
            p.class_
            for p in self.param.params().values()
            if isinstance(p, param.ClassSelector)
            and issubclass(p.class_, Controls)
        ]
        for cls in controls:
            controller_params[cls] = {
                k: params.pop(k) for k, v in dict(params).items()
                if k in cls.param
            }
        super().__init__(**params)
        self._data = df
        self._converter = converter
        self._controls = pn.Param(
            self.param, parameters=['kind', 'x', 'y', 'by', 'groupby'],
            sizing_mode='stretch_width', max_width=300, show_name=False,
        )
        self.param.watch(self._toggle_controls, 'kind')
        self.param.watch(self._check_y, 'y_multi')
        self.param.watch(self._check_by, 'by')
        self._populate()
        self._tabs = pn.Tabs(
            tabs_location='left', width=400
        )
        self._controllers = {
            cls.name.lower(): cls(df, explorer=self, **params)
            for cls, params in controller_params.items()
        }
        self.param.set_param(**self._controllers)
        self.param.watch(self._plot, list(self.param))
        for controller in self._controllers.values():
            controller.param.watch(self._plot, list(controller.param))
        self._alert = pn.pane.Alert(
            alert_type='danger', visible=False, sizing_mode='stretch_width'
        )
        self._layout = pn.Column(
            self._alert,
            pn.Row(
                self._tabs,
                pn.layout.HSpacer(),
                sizing_mode='stretch_width'
            ),
            pn.layout.HSpacer(),
            sizing_mode='stretch_both'
        )
        self._toggle_controls()
        self._plot()

    def _populate(self):
        variables = self._converter.variables
        indexes = getattr(self._converter, "indexes", [])
        variables_no_index = [v for v in variables if v not in indexes]
        for pname in self.param:
            if pname == 'kind':
                continue
            p = self.param[pname]
            if isinstance(p, param.Selector):
                if pname == "x":
                    p.objects = variables
                else:
                    p.objects = variables_no_index

                # Setting the default value if not set
                if (pname == "x" or pname == "y") and getattr(self, pname, None) is None:
                    setattr(self, pname, p.objects[0])

    def _plot(self, *events):
        y = self.y_multi if 'y_multi' in self._controls.parameters else self.y
        if isinstance(y, list) and len(y) == 1:
            y = y[0]
        kwargs = {}
        for p, v in self.param.values().items():
            if isinstance(v, Controls):
                kwargs.update(v.kwargs)

        # Initialize CRS
        crs_kwargs = kwargs.pop('crs_kwargs', {})
        if 'crs' in kwargs:
            if isinstance(kwargs['crs'], type):
                kwargs['crs'] = kwargs['crs'](**crs_kwargs)

        kwargs['min_height'] = 300
        df = self._data
        if len(df) > MAX_ROWS and not (self.kind in STATS_KINDS or kwargs.get('rasterize') or kwargs.get('datashade')):
            df = df.sample(n=MAX_ROWS)
        self._layout.loading = True
        try:
            self._hvplot = _hvPlot(df)(
                kind=self.kind, x=self.x, y=y, by=self.by, groupby=self.groupby, **kwargs
            )
            self._hvpane = pn.pane.HoloViews(
                self._hvplot, sizing_mode='stretch_width', margin=(0, 20, 0, 20)
            ).layout
            self._layout[1][1] = self._hvpane
            self._alert.visible = False
        except Exception as e:
            self._alert.param.set_param(
                object=f'**Rendering failed with following error**: {e}',
                visible=True
            )
        finally:
            self._layout.loading = False

    @property
    def _single_y(self):
        if self.kind in ['labels', 'hexbin', 'heatmap', 'bivariate'] + GRIDDED_KINDS:
            return True
        return False

    def _toggle_controls(self, event=None):
        # Control high-level parameters
        visible = True
        if event and event.new in ('table', 'dataset'):
            parameters = ['kind', 'columns']
            visible = False
        elif event and event.new in TWOD_KINDS:
            parameters = ['kind', 'x', 'y', 'by', 'groupby']
        elif event and event.new in ('hist', 'kde', 'density'):
            self.x = None
            parameters = ['kind', 'y_multi', 'by', 'groupby']
        else:
            parameters = ['kind', 'x', 'y_multi', 'by', 'groupby']
        self._controls.parameters = parameters

        # Control other tabs
        tabs = [('Fields', self._controls)]
        if visible:
            tabs += [
                ('Axes', pn.Param(self.axes, widgets={
                    'xlim': {'throttled': True},
                    'ylim': {'throttled': True}
                }, show_name=False)),
                ('Labels', pn.Param(self.labels, widgets={
                    'rot': {'throttled': True}
                }, show_name=False)),
                ('Style', self.style),
                ('Operations', self.operations),
                # ('Geo', self.geo)
            ]
            if event and event.new not in ('area', 'kde', 'line', 'ohlc', 'rgb', 'step'):
                tabs.insert(5, ('Colormapping', self.colormapping))
        self._tabs[:] = tabs

    def _check_y(self, event):
        if len(event.new) > 1 and self.by:
            self.y = event.old

    def _check_by(self, event):
        if event.new and 'y_multi' in self._controls.parameters and self.y_multi and len(self.y_multi) > 1:
            self.by = []

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def hvplot(self):
        """Return the plot as a HoloViews object.
        """
        return self._hvplot.clone()

    def plot_code(self, var_name='df'):
        """Return a string representation that can be easily copy-pasted
        in a notebook cell to create a plot from a call to the `.hvplot`
        accessor, and that includes all the customized settings of the explorer.

        >>> hvexplorer.plot_code(var_name='data')
        "data.hvplot(x='time', y='value')"

        Parameters
        ----------
        var_name: string
            Data variable name by which the returned string will start.
        """
        settings = self.settings()
        args = ''
        if settings:
            for k, v in settings.items():
                args += f'{k}={v!r}, '
            args = args[:-2]
        return f'{var_name}.hvplot({args})'
    
    def save(self, filename, **kwargs):
        """Save the plot to file.
        
        Calls the `holoviews.save` utility, refer to its documentation
        for a full description of the available kwargs.

        Parameters
        ----------
        filename: string, pathlib.Path or IO object
            The path or BytesIO/StringIO object to save to
        """
        _hv.save(self._hvplot, filename, **kwargs)

    def settings(self):
        """Return a dictionary of the customized settings.
        
        This dictionary can be reused as an unpacked input to the explorer or
        a call to the `.hvplot` accessor.

        >>> hvplot.explorer(df, **settings)
        >>> df.hvplot(**settings)
        """
        settings = {}
        for controller in self._controllers.values():
            params = set(controller.param) - set(['name', 'explorer'])
            for p in params:
                value = getattr(controller, p)
                if value != controller.param[p].default:
                    settings[p] = value
        for p in self._controls.parameters:
            value = getattr(self, p)
            if value != self.param[p].default:
                settings[p] = value
        if 'y_multi' in settings:
            settings['y'] = settings.pop('y_multi')
        settings = {k: v for k, v in sorted(list(settings.items()))}
        return settings


class hvGeomExplorer(hvPlotExplorer):

    kind = param.Selector(default=None, objects=sorted(GEOM_KINDS))

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

    @property
    def _x(self):
        return (self._converter.x or self._converter.indexes[0]) if self.x is None else self.x

    @property
    def _y(self):
        return (self._converter.y or self._converter.indexes[1]) if self.y is None else self.y

    @param.depends('x')
    def xlim(self):
        if self._x == 'index':
            values = self._data.index.values
        else:
            try:
                values = self._data[self._x]
            except:
                return 0, 1
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


class hvDataFrameExplorer(hvPlotExplorer):

    z = param.Selector()

    kind = param.Selector(default='line', objects=sorted(DATAFRAME_KINDS))

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
            try:
                values = self._data[self._x]
            except:
                return 0, 1
        if values.dtype.kind in 'OSU':
            return None
        elif not len(values):
            return (np.nan, np.nan)
        return (np.nanmin(values), np.nanmax(values))

    @param.depends('y', 'y_multi')
    def ylim(self):
        y = self._y
        if not isinstance(y, list):
            y = [y]
        values = [ys for ys in (self._data[y] for y in y) if len(ys)]
        if not len(values):
            return (np.nan, np.nan)
        return max_range([(np.nanmin(vs), np.nanmax(vs)) for vs in values])
