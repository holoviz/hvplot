import holoviews as _hv
import numpy as np
import panel as pn
import param

from holoviews.core.util import datetime_types, dt_to_int, is_number, max_range
from holoviews.element import tile_sources
from holoviews.plotting.util import list_cmaps
from panel.viewable import Viewer

from .converter import HoloViewsConverter as _hvConverter
from .plotting import hvPlot as _hvPlot
from .util import is_geodataframe, is_xarray, instantiate_crs_str

# Defaults
KINDS = {
    # these are for the kind selector
    'dataframe': sorted(
        set(_hvConverter._kind_mapping) -
        set(_hvConverter._gridded_types) -
        set(_hvConverter._geom_types) |
        set(['points'])
    ),
    'gridded': sorted(set(_hvConverter._gridded_types) - set(['dataset'])),
    'geom': _hvConverter._geom_types,
}

KINDS['2d'] = ['bivariate', 'heatmap', 'hexbin', 'labels', 'vectorfield', 'points'] + KINDS['gridded'] + KINDS['geom']
KINDS['stats'] = ['hist', 'kde', 'boxwhisker', 'violin', 'heatmap', 'bar', 'barh']
KINDS['all'] = sorted(set(KINDS['dataframe'] + KINDS['gridded'] + KINDS['geom']))

CMAPS = [cm for cm in list_cmaps() if not cm.endswith('_r_r')]
DEFAULT_CMAPS = _hvConverter._default_cmaps
GEO_FEATURES = [
    'borders', 'coastline', 'land', 'lakes', 'ocean', 'rivers',
    'states', 'grid'
]
GEO_TILES = [None] + sorted(tile_sources)
GEO_KEYS = [
    'crs', 'crs_kwargs', 'projection', 'projection_kwargs',
    'global_extent', 'project', 'features', 'feature_scale', 'tiles'
]
AGGREGATORS = [None, 'count', 'min', 'max', 'mean', 'sum', 'any']
MAX_ROWS = 10000


def explorer(data, **kwargs):
    """Explore your data and design your plot via an interactive user interface.

    This function returns an interactive Panel component that enable you to quickly change the
    settings of your plot via widgets.

    Reference: https://hvplot.holoviz.org/getting_started/explorer.html

    Parameters
    ----------
    data : pandas.DataFrame | xarray.DataArray | xarray.Dataset
        Data structure to explore.
    kwargs : optional
        Arguments that `data.hvplot()` would also accept like `kind='bar'`.

    Returns
    -------
    hvplotExporer
        Panel component to explore the data and design your plot.

    Example
    -------

    >>> import hvplot.pandas
    >>> import pandas as pd
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> hvplot.explorer(df)

    You can also specify initial values

    >>> hvplot.explorer(df, kind='bar', x='x')
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

    responsive = param.Boolean(default=True)

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
        if xlim is not None and is_number(xlim[0]) and is_number(xlim[1]) and xlim[0] != xlim[1]:
            xlim = self._convert_to_int(xlim)
            self.param.xlim.precedence = 0
            self.param.xlim.bounds = xlim
        else:
            self.param.xlim.precedence = -1
        ylim = self.explorer.ylim()
        if ylim is not None and is_number(ylim[0]) and is_number(ylim[1]) and ylim[0] != ylim[1]:
            ylim = self._convert_to_int(ylim)
            self.param.ylim.precedence = 0
            self.param.ylim.bounds = ylim
        else:
            self.param.ylim.precedence = -1

    @staticmethod
    def _convert_to_int(val):
        """
        Converts datetime to int to avoid the error in https://github.com/holoviz/hvplot/issues/964.

        This function is a workaround and should be removed when a better solution is found.

        """

        if isinstance(val[0], datetime_types) and isinstance(val[1], datetime_types):
            val = (dt_to_int(val[0], 'ms'), dt_to_int(val[1], 'ms'))

        return val


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


class Geographic(Controls):

    geo = param.Boolean(default=False, doc="""
        Whether the plot should be treated as geographic (and assume
        PlateCarree, i.e. lat/lon coordinates).""")

    crs = param.Selector(default=None, doc="""
        Coordinate reference system of the data specified as Cartopy
        CRS object, proj.4 string or EPSG code.""")

    crs_kwargs = param.Dict(default={}, doc="""
        Keyword arguments to pass to selected CRS.""")

    projection = param.ObjectSelector(default=None, doc="""
        Projection to use for cartographic plots.""")

    projection_kwargs = param.Dict(default={}, doc="""
        Keyword arguments to pass to selected projection.""")

    global_extent = param.Boolean(default=None, doc="""
        Whether to expand the plot extent to span the whole globe.""")

    project = param.Boolean(default=False, doc="""
        Whether to project the data before plotting (adds initial
        overhead but avoids projecting data when plot is dynamically
        updated).""")

    features = param.ListSelector(default=None, objects=GEO_FEATURES, doc="""
        A list of features or a dictionary of features and the scale
        at which to render it. Available features include 'borders',
        'coastline', 'lakes', 'land', 'ocean', 'rivers' and 'states'.""")

    feature_scale = param.ObjectSelector(default='110m', objects=['110m', '50m', '10m'], doc="""
        The scale at which to render the features.""")

    tiles = param.ObjectSelector(default=None, objects=GEO_TILES, doc="""
        Whether to overlay the plot on a tile source. Tiles sources
        can be selected by name or a tiles object or class can be passed,
        the default is 'Wikipedia'.""")

    @param.depends('geo',  watch=True, on_init=True)
    def _update_crs_projection(self):
        enabled = bool(self.geo or self.project)
        for key in GEO_KEYS:
            self.param[key].constant = not enabled
        self.geo = enabled
        if not enabled:
            return

        from cartopy.crs import CRS
        crs_list = sorted(
            k for k in param.concrete_descendents(CRS).keys()
            if not k.startswith('_') and k != 'CRS'
        )
        crs_list.insert(0, 'GOOGLE_MERCATOR')
        crs_list.insert(0, 'PlateCarree')
        crs_list.remove('PlateCarree')

        self.param.crs.objects = crs_list
        self.param.projection.objects = crs_list
        if self.projection is None:
            self.projection = crs_list[0]

        if self.global_extent is None:
            self.global_extent = True

        if self.features is None:
            self.features = ['coastline']


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


class Advanced(Controls):

    opts = param.Dict(default={}, label='HoloViews .opts()', doc="""
        Options applied via HoloViews .opts().
        Examples:
        - image: {"color_levels": 11}
        - line: {"line_dash": "dashed"}
        - scatter: {'size': 5, 'marker': '^'}""")


class StatusBar(param.Parameterized):

    live_update = param.Boolean(default=True, doc="""
        Whether to automatically update the plot when a param is changed""")


class hvPlotExplorer(Viewer):

    kind = param.Selector()

    x = param.Selector()

    y = param.Selector()

    y_multi = param.ListSelector(default=[], label='Y')

    by = param.ListSelector(default=[])

    groupby = param.ListSelector(default=[])

    # Controls that will show up as new tabs, must be ClassSelector

    axes = param.ClassSelector(class_=Axes)

    colormapping = param.ClassSelector(class_=Colormapping)

    labels = param.ClassSelector(class_=Labels)

    geographic = param.ClassSelector(class_=Geographic)

    operations = param.ClassSelector(class_=Operations)

    statusbar = param.ClassSelector(class_=StatusBar)

    style = param.ClassSelector(class_=Style)

    advanced = param.ClassSelector(class_=Advanced)

    code = param.String(precedence=-1, doc="""
        Code to generate the plot.""")

    @classmethod
    def from_data(cls, data, **params):
        if is_geodataframe(data):
            # cls = hvGeomExplorer
            raise TypeError('GeoDataFrame objects not yet supported.')
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
        statusbar_params = {
            k: params.pop(k)
            for k in params.copy()
            if k in StatusBar.param
        }
        converter = _hvConverter(
            df, x, y,
            **{k: v for k, v in params.items() if k not in ('x', 'y', 'y_multi')}
        )
        # Collect kwargs passed to the constructor but meant for the controls
        extras = {
            k: params.pop(k)
            for k in params.copy()
            if k not in self.param
        }
        super().__init__(**params)
        self._data = df
        self._converter = converter
        groups = {group: KINDS[group] for group in self._groups}
        self._controls = pn.Param(
            self.param, parameters=['kind', 'x', 'y', 'groupby', 'by'],
            sizing_mode='stretch_width', show_name=False,
            widgets={'kind': {'options': [], 'groups': groups}}
        )
        self.param.watch(self._toggle_controls, 'kind')
        self.param.watch(self._check_y, 'y_multi')
        self.param.watch(self._check_by, 'by')
        self._populate()
        self._control_tabs = pn.Tabs(
            tabs_location='left', width=425
        )
        self.statusbar = StatusBar(**statusbar_params)
        self._statusbar = pn.Param(self.statusbar, show_name=False, default_layout=pn.Row)
        controls = [
            p.class_
            for p in self.param.objects().values()
            if isinstance(p, param.ClassSelector)
            and issubclass(p.class_, Controls)
        ]
        controller_params = {}
        for cls in controls:
            controller_params[cls] = {
                k: extras.pop(k)
                for k in extras.copy()
                if k in cls.param
            }
        if extras:
            raise TypeError(
                f'__init__() got keyword(s) not supported by any control: {extras}'
            )
        self._controllers = {
            cls.name.lower(): cls(df, explorer=self, **cparams)
            for cls, cparams in controller_params.items()
        }
        self.param.update(**self._controllers)
        self.param.watch(self._refresh, list(self.param))
        for controller in self._controllers.values():
            controller.param.watch(self._refresh, list(controller.param))
        self.statusbar.param.watch(self._refresh, list(self.statusbar.param))
        self._alert = pn.pane.Alert(
            alert_type='danger', visible=False, sizing_mode='stretch_width'
        )
        self._hv_pane = pn.pane.HoloViews(sizing_mode='stretch_width', margin=(5, 20, 5, 20))
        self._code_pane = pn.pane.Markdown(sizing_mode='stretch_width', margin=(5, 20, 0, 20))
        self._layout = pn.Column(
            self._alert,
            pn.Row(
                self._control_tabs,
                pn.Tabs(('Plot', self._hv_pane), ('Code', self._code_pane)),
                sizing_mode='stretch_width',
            ),
            self._statusbar,
            pn.layout.HSpacer(),
            sizing_mode='stretch_both'
        )

        # initialize
        self.param.trigger('kind')

    def _populate(self):
        """
        Populates the options of the controls based on the data type.
        """
        variables = self._converter.variables
        indexes = getattr(self._converter, 'indexes', [])
        variables_no_index = [v for v in variables if v not in indexes]
        for pname in self.param:
            if pname == 'kind':
                continue
            p = self.param[pname]
            if isinstance(p, param.Selector):
                if pname == 'x':
                    p.objects = variables
                else:
                    p.objects = variables_no_index

                # Setting the default value if not set
                if (pname == 'x' or pname == 'y') and getattr(self, pname, None) is None:
                    setattr(self, pname, p.objects[0])

    def _plot(self, *events):
        y = self.y_multi if 'y_multi' in self._controls.parameters else self.y
        if isinstance(y, list) and len(y) == 1:
            y = y[0]
        kwargs = {}
        for v in self.param.values().values():
            # Geo is not enabled so not adding it to kwargs
            if isinstance(v, Geographic) and not v.geo:
                continue

            if isinstance(v, Advanced):
                opts_kwargs = v.kwargs.get('opts', {})
            elif isinstance(v, Controls):
                kwargs.update(v.kwargs)

        if kwargs.get('geo'):
            if 'crs' not in kwargs:
                xmax = np.max(np.abs(self.xlim()))
                self.geographic.crs = 'PlateCarree' if xmax <= 360 else 'GOOGLE_MERCATOR'
                kwargs['crs'] = self.geographic.crs
            for key in ['crs', 'projection']:
                crs_kwargs = kwargs.pop(f'{key}_kwargs', {})
                kwargs[key] = instantiate_crs_str(kwargs.pop(key), **crs_kwargs)

            feature_scale = kwargs.pop('feature_scale', None)
            kwargs['features'] = {feature: feature_scale for feature in kwargs.pop('features', [])}

        kwargs['min_height'] = 400
        df = self._data
        if len(df) > MAX_ROWS and not (self.kind in KINDS['stats'] or kwargs.get('rasterize') or kwargs.get('datashade')):
            df = df.sample(n=MAX_ROWS)
        self._layout.loading = True
        try:
            self._hvplot = _hvPlot(df)(
                kind=self.kind, x=self.x, y=y, by=self.by, groupby=self.groupby, **kwargs
            )
            if opts_kwargs:
                self._hvplot.opts(**opts_kwargs)
            self._hv_pane.object = self._hvplot
            self._alert.visible = False
        except Exception as e:
            self._alert.param.update(
                object=f'**Rendering failed with following error**: {e}',
                visible=True
            )
        finally:
            self._layout.loading = False

    def _refresh(self, *events):
        if not self.statusbar.live_update:
            return
        self._plot()
        with param.parameterized.discard_events(self):
            self.code = self.plot_code()
        self._code_pane.object = f"""```python\n{self.code}\n```"""

    @property
    def _var_name(self):
        return 'data'

    @property
    def _single_y(self):
        if self.kind in KINDS['2d']:
            return True
        return False

    @property
    def _groups(self):
        raise NotImplementedError('Must be implemented by subclasses.')

    def _toggle_controls(self, event=None):
        # Control high-level parameters
        visible = True
        if event and event.new in ('table', 'dataset'):
            parameters = ['kind', 'columns']
            visible = False
        elif event and event.new in KINDS['2d']:
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
                ('Geographic', self.geographic),
                ('Advanced', self.advanced),
            ]
            if event and event.new not in ('area', 'kde', 'line', 'ohlc', 'rgb', 'step'):
                tabs.insert(5, ('Colormapping', self.colormapping))
        self._control_tabs[:] = tabs

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

    def plot_code(self, var_name=None):
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
        settings_args = ''
        if settings:
            settings_args = self._build_kwargs_string(settings)
        snippet = f'{var_name or self._var_name}.hvplot(\n{settings_args}\n)'
        opts = self.advanced.opts
        if opts:
            opts_args = self._build_kwargs_string(opts)
            snippet += f'.opts(\n{opts_args}\n)'
        return snippet

    def _build_kwargs_string(self, kwargs):
        args = ''
        if kwargs:
            for k, v in kwargs.items():
                args += f'    {k}={v!r},\n'
            args = args[:-1]
        return args

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
            params = set(controller.param) - {'name', 'explorer'}
            for p in params:
                value = getattr(controller, p)
                if value != controller.param[p].default:
                    settings[p] = value
        for p in self._controls.parameters:
            value = getattr(self, p)
            if value != self.param[p].default or p == 'kind':
                settings[p] = value
        if 'y_multi' in settings:
            settings['y'] = settings.pop('y_multi')
        settings.pop('opts', None)
        settings = {k: v for k, v in sorted(list(settings.items()))}
        return settings


class hvGeomExplorer(hvPlotExplorer):

    kind = param.Selector(default=None, objects=KINDS['all'])

    @property
    def _var_name(self):
        return 'gdf'

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

    @property
    def _groups(self):
        return ['gridded', 'dataframe']

class hvGridExplorer(hvPlotExplorer):

    kind = param.Selector(default='image', objects=KINDS['all'])

    def __init__(self, ds, **params):
        import xarray as xr
        var_name_suffix = ''
        if isinstance(ds, xr.Dataset):
            data_vars = list(ds.data_vars)
            if len(data_vars) == 1:
                ds = ds[data_vars[0]]
                var_name_suffix = f"['{data_vars[0]}']"
            else:
                ds = ds.to_array('variable').transpose(..., 'variable')
                var_name_suffix = ".to_array('variable').transpose(..., 'variable')"
        if 'kind' not in params:
            params['kind'] = 'image'
        self._var_name_suffix = var_name_suffix
        super().__init__(ds, **params)

    @property
    def _var_name(self):
        if self._var_name_suffix:
            return f'ds{self._var_name_suffix}'
        else:
            return 'da'

    @property
    def _x(self):
        return (self._converter.x or self._converter.indexes[0]) if self.x is None else self.x

    @property
    def _y(self):
        return (self._converter.y or self._converter.indexes[1]) if self.y is None else self.y

    @param.depends('x')
    def xlim(self):
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

    @property
    def _groups(self):
        return ['gridded', 'dataframe', 'geom']

    def _populate(self):
        variables = self._converter.variables
        indexes = getattr(self._converter, 'indexes', [])
        variables_no_index = [v for v in variables if v not in indexes]
        for pname in self.param:
            if pname == 'kind':
                continue
            p = self.param[pname]
            if isinstance(p, param.Selector):
                if pname in ['x', 'y', 'groupby', 'by']:
                    p.objects = indexes
                else:
                    p.objects = variables_no_index

                # Setting the default value if not set
                if pname == 'x' and getattr(self, pname, None) is None:
                    setattr(self, pname, p.objects[0])
                elif pname == 'y' and getattr(self, pname, None) is None:
                    setattr(self, pname, p.objects[1])
                elif pname == 'groupby' and len(getattr(self, pname, [])) == 0 and len(p.objects) > 2:
                    setattr(self, pname, p.objects[2:])


class hvDataFrameExplorer(hvPlotExplorer):

    z = param.Selector()

    kind = param.Selector(default='line', objects=KINDS['all'])

    @property
    def _var_name(self):
        return 'df'

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

    @property
    def _groups(self):
        return ['dataframe']

    @param.depends('x')
    def xlim(self):
        if self._x == 'index':
            values = self._data.index.values
        else:
            try:
                values = self._data[self._x]
            except:
                return 0, 1
        # for dask series; else it cannot get length
        if hasattr(values, 'compute_chunk_sizes'):
            values = values.compute_chunk_sizes()
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
