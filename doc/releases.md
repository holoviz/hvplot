# Releases

## Version 0.8.0

**May 6, 2022**

The 0.8.0 release is a minor release with some exciting new features and a large number of bug fixes and enhancements. Many thanks to @FabianHofmann, @jomey, @ablythed, @jlstevens, @Hoxbro, @michaelaye, @MridulS, @ppwadhwa, @maximlt, @philippjfr for contributing!

Main new features:
- Add ability to call ``.interactive()`` on bound functions ([#720](https://github.com/holoviz/hvplot/pull/720))
- Add support to the Matplotlib and Plotly backends ([#653](https://github.com/holoviz/hvplot/pull/653))
- Add the ``hvPlotExplorer``, a Panel UI component designed to explore data ([#638](https://github.com/holoviz/hvplot/pull/638), [#639](https://github.com/holoviz/hvplot/pull/639), [#651](https://github.com/holoviz/hvplot/pull/651), [#710](https://github.com/holoviz/hvplot/pull/710), [#726](https://github.com/holoviz/hvplot/pull/726))

Enhancements:
- Interactive:
  - Allow using getitem on an accessor in interactive ([#633](https://github.com/holoviz/hvplot/pull/633))
  - Allow attribute access on ufunc on interactive ([#635](https://github.com/holoviz/hvplot/pull/635))
  - Enhancements for ``interactive`` API ([#640](https://github.com/holoviz/hvplot/pull/640))
  - Flatten op_args to be able to find nested widgets ([#699](https://github.com/holoviz/hvplot/pull/699))
- Allow dynspread to be used with ``rasterize`` ([#637](https://github.com/holoviz/hvplot/pull/637))
- Add a title to xarray plots with scalar coords ([#659](https://github.com/holoviz/hvplot/pull/659))
- Adding ``datashade`` and ``rasterize`` options to scatter_matrix ([#495](https://github.com/holoviz/hvplot/pull/495))
- Update the default internal value of ``clim`` to support Matplotlib ([#679](https://github.com/holoviz/hvplot/pull/679))
- Ensure bokeh/panel extension is loaded only once ([#686](https://github.com/holoviz/hvplot/pull/686))
- Add support for planar layout from Networkx ([#700](https://github.com/holoviz/hvplot/pull/700))
- Wrap color in ``hv.dim`` when it matches a dimension/column ([#717](https://github.com/holoviz/hvplot/pull/717))
- Expose datashader line_width and rescale_discrete_levels options ([#731](https://github.com/holoviz/hvplot/pull/731))
- Improve array-like handling for x and y inputs ([#714](https://github.com/holoviz/hvplot/pull/714))

Fixes:
- Interactive:
  - Interactive fixes ([#630](https://github.com/holoviz/hvplot/pull/630))
  - Fix for interactive transform ([#632](https://github.com/holoviz/hvplot/pull/632))
  - Fix issue with accessors on interactive ([#641](https://github.com/holoviz/hvplot/pull/641))
  - Consistently dereference attribute access ([#642](https://github.com/holoviz/hvplot/pull/642))
- State that the data cannot be symmetric if it's empty ([#680](https://github.com/holoviz/hvplot/pull/680))
- Disable hover on errorbars plot ([#721](https://github.com/holoviz/hvplot/pull/721))
- Fix application of the scale argument for geoviews features ([#725](https://github.com/holoviz/hvplot/pull/725))

Documentation:
- Add scatter matrix reference ([#689](https://github.com/holoviz/hvplot/pull/689))
- Plotting user guide enhancement ([#694](https://github.com/holoviz/hvplot/pull/694))
- Download a tutorial file with the right filename ([#711](https://github.com/holoviz/hvplot/pull/711))
- Add more imports to try/except import check ([#693](https://github.com/holoviz/hvplot/pull/693))
- Various minor documentation enhancements and fixes ([#625](https://github.com/holoviz/hvplot/pull/625), [#643](https://github.com/holoviz/hvplot/pull/643), [#644](https://github.com/holoviz/hvplot/pull/644), [#663](https://github.com/holoviz/hvplot/pull/663), [#678](https://github.com/holoviz/hvplot/pull/678), [#722](https://github.com/holoviz/hvplot/pull/722))

Maintenance:
- Drop support for Python 2.7, minimum supported version is now Python 3.6 ([#702](https://github.com/holoviz/hvplot/pull/702))
- Changed to ``packaging.version`` ([#708](https://github.com/holoviz/hvplot/pull/708))

## Version 0.7.3

This is a minor release focusing on greatly improving the
[`.interactive()`](https://hvplot.holoviz.org/user_guide/Interactive.html)
API for flexibly building simple apps using widget controls. Thanks to
@jbednar and @jlstevens for a few small fixes and many thanks to
@philippjfr for all the rest!

Features:

- Improved `.interactive` Dataframe support: max_rows display, column
  access ([#640](https://github.com/holoviz/hvplot/pull/640))
- Improved accesssor and attribute behavior for `.interactive`
  ([#633](https://github.com/holoviz/hvplot/pull/633),
  [#635](https://github.com/holoviz/hvplot/pull/635),
  [#641](https://github.com/holoviz/hvplot/pull/641),
  [#642](https://github.com/holoviz/hvplot/pull/642))
- Add `.holoviews()` terminal method to `.interactive` pipelines
- Add support for kwargs to `.interactive.layout`
- Misc fixes to `.interactive` API
([#630](https://github.com/holoviz/hvplot/pull/630),
[#632](https://github.com/holoviz/hvplot/pull/632))
- Allow `dynspread=True` to be used with `rasterize=True` (now that
  Datashader supports it)

## Version 0.7.2

This is  a minor release with a number of bug fixes and enhancements.
Many thanks to @StefanBrand, @loicduffar, @brl0, @michaelaye,
@aaronspring, @toddrjen, @raybellwaves, @jlstevens, @jbednar and
@philippjfr for contributing.

Features:

- Add support for geographic features ([#622](https://github.com/holoviz/hvplot/pull/622))
- Added support for OHLC plot ([#623](https://github.com/holoviz/hvplot/pull/623))

Enhancements:

- Support setting options for diagonal plots in ``scatter_matrix`` ([#602](https://github.com/holoviz/hvplot/pull/602))
- Take ``group_label`` from columns if available ([#615](https://github.com/holoviz/hvplot/pull/615))
- Add kwargs to ``interactive.layout()``

Bug fixes:

- Fix support for ``clim`` on ``contours`` ([#587](https://github.com/holoviz/hvplot/pull/587))
- Adding default coordinates to datasets with missing coords ([#605](https://github.com/holoviz/hvplot/pull/605))
- Do not plot ``streamz`` example point ([#614](https://github.com/holoviz/hvplot/pull/614))
- Fix passing in multiple z-values ([#616](https://github.com/holoviz/hvplot/pull/616))
- Ensure ``violin`` and ``boxplot`` color is applied ([#619](https://github.com/holoviz/hvplot/pull/))
- Ensure categorical colormapping is applied during ``datashade`` ([#621](https://github.com/holoviz/hvplot/pull/621))

Compatibility:

- Switch default tile source to ``OSM`` (since ``Wikipedia`` is no longer available) ([#610](https://github.com/holoviz/hvplot/pull/610))

Documentation:

- Correctly document .hist rather than ``.histogram`` ([#571](https://github.com/holoviz/hvplot/pull/571))
- Use strings rather than bytes when referring to airplane dataset columns ([#538](https://github.com/holoviz/hvplot/issues/538))
- Preserve function signature and docstring in ``with_hv_extension`` ([#601](https://github.com/holoviz/hvplot/pull/601))
- Add ``hover_cols`` example ([#612](https://github.com/holoviz/hvplot/pull/612))
- Switch to pydata sphinx theme ([#613](https://github.com/holoviz/hvplot/pull/613))
- Update available options in customization docs ([#620](https://github.com/holoviz/hvplot/pull/620))

## Version 0.7.1

Major new features:

- Add Ibis backend, providing hvPlot features for lazy SQL queries ([#507](https://github.com/holoviz/hvplot/pull/507))

Enhancements:

- Cycles for continuous colormaps ([#548)
- Validate by column(s) ([#565)
- Add `hover='vline'` `hover='hline'` options to expose Bokeh HoverTool mode ([#493](https://github.com/holoviz/hvplot/pull/493))
- Support streaming plots from HoloViews streams (not needing a streamz source) ([#542](https://github.com/holoviz/hvplot/pull/542))

Bug fixes:

- Drop tuple NetworkX attributes to avoid errors ([#549](https://github.com/holoviz/hvplot/pull/549))
- Cast types after applying melt to data ([#566](https://github.com/holoviz/hvplot/pull/566))

## Version 0.7.0

Thanks to @philippjfr for managing this release and implementing most
of the features, and to @jbednar, @ahuang11, and @AurelienSciarra for
contributions.

Major new features:

- Powerful new `.interactive()` API for building easy apps ([#505](https://github.com/holoviz/hvplot/pull/505), [#523](https://github.com/holoviz/hvplot/pull/523))
- New `transforms` argument to transform data in `.hvplot()` calls ([#526](https://github.com/holoviz/hvplot/pull/526))

Other new features and enhancements:

- Support passing geographic projections as strings ([#372](https://github.com/holoviz/hvplot/pull/372))
- Improved data selection, e.g. for filtering on metadata ([#522](https://github.com/holoviz/hvplot/pull/522))
- Provide color_key to datashade as well as cmap, for convenience ([#525](https://github.com/holoviz/hvplot/pull/525))
- Update param warnings to new API ([#528](https://github.com/holoviz/hvplot/pull/528))
- Replace TravisCI tests with GitHub Actions ([#524](https://github.com/holoviz/hvplot/pull/524))

Bug fixes:

- Fix for specifying ``hover_cols`` ([#504](https://github.com/holoviz/hvplot/pull/504))
- Remove outdated reference to `__main__` console script ([#494](https://github.com/holoviz/hvplot/pull/494))
- Misc doc fixes, including to Streaming.ipynb ([#481](https://github.com/holoviz/hvplot/pull/481), [#511](https://github.com/holoviz/hvplot/pull/511))
- Handle ``node_shape`` for networkx ([#527](https://github.com/holoviz/hvplot/pull/527))

## Version 0.6.0

This release includes major contributions from @philippjfr (overall
maintenance and bugfixes) and @jsignell (reference gallery), plus
additional contributions from @slamer59 (environment), @anitagraser
(examples), @itcarroll (color_key alias), @Timothy-W-Hilton (bugfix),
@jbednar (bugfix), @SandervandenOord (fontscale), and @jordansamuels
(doc fixes).

New features:

- Improved ``save`` and ``show`` utilities ([#451](https://github.com/holoviz/hvplot/pull/451))
- Improved compatibility for tab completion ([#411](https://github.com/holoviz/hvplot/pull/411))
- Major performance enhancement with Datashader in some cases ([#465](https://github.com/holoviz/hvplot/pull/465))
- Add support for cuDF ([#454](https://github.com/holoviz/hvplot/pull/454), [#466](https://github.com/holoviz/hvplot/pull/466))
- Support `by` argument for categorical aggregation ([#461](https://github.com/holoviz/hvplot/pull/461))
- Support ``color_key`` alias ([#446](https://github.com/holoviz/hvplot/pull/446), [#458](https://github.com/holoviz/hvplot/pull/458))
- Support ``spatialpandas`` for large sets of polygons ([#459](https://github.com/holoviz/hvplot/pull/459))
- Add ``fontscale`` keyword ([#397](https://github.com/holoviz/hvplot/pull/397))

Bug fixes and compatibility:

- Fixed ``'title_format'`` deprecation warning ([#428](https://github.com/holoviz/hvplot/pull/428))
- Avoid sorting overlays, to make color cycles consistent ([#475](https://github.com/holoviz/hvplot/pull/475))
- Fix inference of non-declared index coordinates ([#329](https://github.com/holoviz/hvplot/pull/329))
- Improved handling of indexes on flattened grid ([#452](https://github.com/holoviz/hvplot/pull/452))
- Preserve ``Dataset.pipeline`` ([#453](https://github.com/holoviz/hvplot/pull/453))
- Fixes for option handling ([#458](https://github.com/holoviz/hvplot/pull/458))

Documentation:

- Added (a start to) a reference gallery
- Added heat and trees example to topics ([#378](https://github.com/holoviz/hvplot/pull/378))
- Replaced sphinx_pyviz_theme with sphinx_holoviz_theme ([#366](https://github.com/holoviz/hvplot/pull/366))
- Removed references to pyviz ([#373](https://github.com/holoviz/hvplot/pull/373))
- Fix networkx documentation ([#476](https://github.com/holoviz/hvplot/pull/476))

## Version 0.5.2

This release mostly includes contributions from @jsignell.

- Allow tile sources to be objects as well as strings ([#345](https://github.com/holoviz/hvplot/pull/345))
- Set ``geo=True`` by default for coastline ([#344](https://github.com/holoviz/hvplot/pull/344))
- Add ``check_symmetric_max`` limit for working with large data ([#340](https://github.com/holoviz/hvplot/pull/340))
- Expose plot at top level, to support `pd.options.plotting.backend = 'hvplot'` ([#347](https://github.com/holoviz/hvplot/pull/347))
- Misc bug fixes ([#341](https://github.com/holoviz/hvplot/pull/341), [#343](https://github.com/holoviz/hvplot/pull/343), [#346](https://github.com/holoviz/hvplot/pull/346))

## Version 0.5.1

Minor release with updates to continuous integration setup (from @jsignell).

## Version 0.5.0

This is a major release that includes bug fixes, changes to default behavior, and enhancements.

Features:
 - Widget handling capabilities to facilitate interactivity ([#323](https://github.com/holoviz/hvplot/pull/323), [#331](https://github.com/holoviz/hvplot/pull/331))
 - New default colormaps ([#258](https://github.com/holoviz/hvplot/pull/258), [#316](https://github.com/holoviz/hvplot/pull/316), [#206](https://github.com/holoviz/hvplot/pull/206)) 
 - long_name(units) used to label xarray objects ([#173](https://github.com/holoviz/hvplot/pull/173))
 - Derived datetime accessor handlind ([#263](https://github.com/holoviz/hvplot/pull/263), [#286](https://github.com/holoviz/hvplot/pull/286))
 - `coastline` and `tiles` options for easy geo plots.
 - Automatic date sorting ([#259](https://github.com/holoviz/hvplot/pull/259))
 - Allow use of strings as aggregators for datashader ([#257](https://github.com/holoviz/hvplot/pull/257))

## Version 0.4.0

This is a major release which includes the addition of a networkx
plotting API and a number of important bug fixes.

Features:

- A new NetworkX interface providing equivalents for the networkx plotting module ([#152](https://github.com/holoviz/hvplot/pull/152), [#154](https://github.com/holoviz/hvplot/pull/154))

Fixes:

- Fixed handling of labelled property to hide axis labels ([#142](https://github.com/holoviz/hvplot/pull/142))
- Fixed handling of DataArrays and groupby on RGB plots ([#138](https://github.com/holoviz/hvplot/pull/138), [#141](https://github.com/holoviz/hvplot/pull/141))
- Allow setting axis position ([#149](https://github.com/holoviz/hvplot/pull/149))
- Fixes for setting the axis positions ([#145](https://github.com/holoviz/hvplot/pull/145))

## Version 0.3.0

This release includes a number of major improvements to the documentation and core functionality as well as a variety of bug fixes.

- Added improved docstrings including all available options ([#103](https://github.com/pyviz/hvplot/pull/103), [#134](https://github.com/pyviz/hvplot/pull/134))
- Added support for tab-completion in interactive environments such as IPython and Jupyter notebooks ([#134](https://github.com/pyviz/hvplot/pull/134))
- Added support for ``rgb`` ([#137](https://github.com/pyviz/hvplot/pull/137)) and ``labels`` ([#98](https://github.com/pyviz/hvplot/pull/98)) plot types
- Exposed bokeh styling options for all plot types ([#134](https://github.com/pyviz/hvplot/pull/134))
- Compatibility with latest HoloViews/GeoViews releases ([#113](https://github.com/pyviz/hvplot/pull/113), [#118](https://github.com/pyviz/hvplot/pull/118), [#134](https://github.com/pyviz/hvplot/pull/134))
- Added control over tools ([#120](https://github.com/pyviz/hvplot/pull/120)) and legend position ([#119](https://github.com/pyviz/hvplot/pull/119))

