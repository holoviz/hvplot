# Releases

See [the HoloViz blog](https://blog.holoviz.org/#category=hvplot) for a visual summary of the major features added in a selection of releases.

## Version 0.10.0 (2024-05-06)

This minor release brings a number of enhancements and bugfixes, checkout the [release blog post](https://blog.holoviz.org/posts/hvplot_release_0.10/) for a visual summary of the most important enhancements.

- 🧰 Improving the contributor experience: moving away from `pyctdev` to a more usual and easier approach, and adopt `ruff` as a linter and formatter
- 📦 Modernizing hvPlot's packaging: migrating to `pyproject.toml`
- 📖 Improving the documentation: adding a user guide on large time-series and improving the geographic user guide
- 📈 Enhancing the plotting API: in part to support the [NumFocus SDG](https://opencollective.com/holoviz/projects/holoviz-sdg-2023-round-3) project that aims to modernize the [HoloViz Examples](https://examples.holoviz.org)
- 🐛 Fixing bugs!

Many thanks to @ahuang11, @droumis, @Hoxbro, @jsignell, and @maximlt for their contributions.

Governance:

- Andrew (@ahuang11) promoted as Maintainer! ([#1267](https://github.com/holoviz/hvplot/pull/1267))

Enhancements:

- Add `bgcolor` parameter to set the background color ([#1308](https://github.com/holoviz/hvplot/pull/1308))
- Add `robust` parameter, similarly to Xarray ([#1291](https://github.com/holoviz/hvplot/pull/1291))
- Add `tiles_opts` parameter to customize the tiles ([#1299](https://github.com/holoviz/hvplot/pull/1299))
- Add support to `xyzservices` tiles ([#1307](https://github.com/holoviz/hvplot/pull/1307))
- Allow to set the `downsample` algorithm as string input ([#1314](https://github.com/holoviz/hvplot/pull/1314))
- Allow `crs` as Cartopy class name to match `projection` ([#1332](https://github.com/holoviz/hvplot/pull/1332))

Bug Fixes:

- Fix saving Panel objects with `hvplot.save` ([#1297](https://github.com/holoviz/hvplot/pull/1297))
- Fix setting `group_label` when plotting a histogram ([#1310](https://github.com/holoviz/hvplot/pull/1310))
- Fix the support of HoloViews ImageStack support and usage of `aggregator` and `by` ([#1316](https://github.com/holoviz/hvplot/pull/1316))
- Fix handling of EPSG codes ([#1330](https://github.com/holoviz/hvplot/pull/1330))
- Explorer: fix handling of Xarray objects that have dims without coords ([#1334](https://github.com/holoviz/hvplot/pull/1334))

Compatibility:

- Minor changes in preparation of the HoloViews Pandas index refactor ([#1281](https://github.com/holoviz/hvplot/pull/1281))

Documentation:

- Add user guide for working with large time-series datasets ([#1302](https://github.com/holoviz/hvplot/pull/1302))
- Clarify the geographic user guide ([#1269](https://github.com/holoviz/hvplot/pull/1269), [#1299](https://github.com/holoviz/hvplot/pull/1299))
- Misc ([#1266](https://github.com/holoviz/hvplot/pull/1266), [#1268](https://github.com/holoviz/hvplot/pull/1268), [#1319](https://github.com/holoviz/hvplot/pull/1319))

Infrastructure / Tests:

- Migrate to pyproject.toml and improve the contributor experience ([#1296](https://github.com/holoviz/hvplot/pull/1296), [#1322](https://github.com/holoviz/hvplot/pull/1322))
- Format and lint the code base with `ruff` ([#1320](https://github.com/holoviz/hvplot/pull/1320))
- Pin intake to version 2.0.0 ([#1275](https://github.com/holoviz/hvplot/pull/1275))
- Fix the test suite after the latest Dask release ([#1298](https://github.com/holoviz/hvplot/pull/1298))
- Remove the `examples` folder ([#1287](https://github.com/holoviz/hvplot/pull/1287))
- Install the tests dependencies primarily with pip ([#1276](https://github.com/holoviz/hvplot/pull/1276))
- Misc ([#1317](https://github.com/holoviz/hvplot/pull/1317), [#1321](https://github.com/holoviz/hvplot/pull/1321), [#1323](https://github.com/holoviz/hvplot/pull/1323), [#1324](https://github.com/holoviz/hvplot/pull/1324), [#1327](https://github.com/holoviz/hvplot/pull/1327))

[Full Changelog](https://github.com/holoviz/hvplot/compare/v0.9.2...v0.9.3)

## Version 0.9.2 (2024-01-29)

The 0.9.2 release is a patch release that brings a few bugfixes and documentation improvements, improving `Polars` support and documentation. Many thanks to @kevinheavey (first contribution!), @MarcoGorelli, @Hoxbro, and @maximlt for their contributions.

Bug fixes:

- Correctly fall back to all numeric Polars columns when `y` is not specified ([#1247](https://github.com/holoviz/hvplot/pull/1247))

Documentation:

- Better expose Polars support ([#1262](https://github.com/holoviz/hvplot/pull/1262))
- Rename the `Pandas` reference section to `Tabular` ([#1260](https://github.com/holoviz/hvplot/pull/1260))
- Add roadmap for 2024 ([#1253](https://github.com/holoviz/hvplot/pull/1253))
- Various small changes ([#1255](https://github.com/holoviz/hvplot/pull/1255) and [#1261](https://github.com/holoviz/hvplot/pull/1261))

Infrastructure / Tests:

- Add downstream Polars test ([#1243](https://github.com/holoviz/hvplot/pull/1243))
- Compatibility with Pandas 2.2 ([#1257](https://github.com/holoviz/hvplot/pull/1257))
- Dynamically generate the unit test matrix and add a cache option ([#1235](https://github.com/holoviz/hvplot/pull/1235))

[Full Changelog](https://github.com/holoviz/hvplot/compare/v0.9.1...v0.9.2)

## Version 0.9.1 (2023-12-22)

The 0.9.1 release brings a number of enhancements, bugfixes and documentation improvements. Many thanks to @iuryt (first contribution!), @MarcoGorelli (first contribution!), @ahuang11, @Hoxbro and @maximlt for their contributions.

Enhancements:

- Explorer: give more space to the plot and various UI tweaks ([#1197](https://github.com/holoviz/hvplot/pull/1197), [#1198](https://github.com/holoviz/hvplot/pull/1198), [#1199](https://github.com/holoviz/hvplot/pull/1199), [#1225](https://github.com/holoviz/hvplot/pull/1225))
- Explorer: disable the geographic controls when `geoviews` is not installed ([#1223](https://github.com/holoviz/hvplot/pull/1223))
- Explorer: change the default plot type from `line` to `scatter` ([#1228](https://github.com/holoviz/hvplot/pull/1228))
- Support `polars` objects in the `hvplot.plot` entrypoint ([#1219](https://github.com/holoviz/hvplot/pull/1219), [#1222](https://github.com/holoviz/hvplot/pull/1222))

Bug fixes:

- Fix ignoring `hover_cols` in OHLC plots ([#1216](https://github.com/holoviz/hvplot/pull/1216))
- Fix considering datashaded plots with one *y* variable as categorical ([#1231](https://github.com/holoviz/hvplot/pull/1231))
- Fix displaying Panel objects returned by hvPlot with `show` ([#1230](https://github.com/holoviz/hvplot/pull/1230))

Documentation:

- Replace Google Analytics with GoatCounter ([#1224](https://github.com/holoviz/hvplot/pull/1224))
- Indicate that *Stamen* tiles require a *Stadia* account ([#1226](https://github.com/holoviz/hvplot/pull/1226))
- Reintroduce colorbars in the Matplotlib guide ([#1229](https://github.com/holoviz/hvplot/pull/1229))
- Misc ([#1186](https://github.com/holoviz/hvplot/pull/1186), [#1195](https://github.com/holoviz/hvplot/pull/1195))

Maintenance:

- Bump the minimum Param version to `1.12.0` ([#1227](https://github.com/holoviz/hvplot/pull/1227))

[Full changelog](https://github.com/holoviz/hvplot/compare/v0.9.0...v0.9.1)

## Version 0.9.0 (2023-10-16)

The 0.9.0 release is a minor release with some exciting new features and a large number of bug fixes and enhancements. Many thanks to @rdesai9 (first contribution!), @dogbunny (first contribution!), @bikegeek (first contribution!), @ahuang11, @droumis, @Hoxbro, @MarcSkovMadsen, @maximlt  and @philippjfr for their contributions. A special thanks to @ahuang11 and @Hoxbro without who these release notes would be much shorter!

New features:

- The *Explorer* has been extended with the following features:
  - Support for Xarray data, enhanced geographic support and add a *live update* checkbox ([#1141](https://github.com/holoviz/hvplot/pull/1141))
  - Display the code snippet within a tab ([#1156](https://github.com/holoviz/hvplot/pull/1156))
  - Allow defining options passed to `plot.opts()` ([#1171](https://github.com/holoviz/hvplot/pull/1171))
- Add experimental Fugue integration ([#1102](https://github.com/holoviz/hvplot/pull/1102))
- Add basic Polars integration ([#1129](https://github.com/holoviz/hvplot/pull/1129))

Enhancements:

- Add `.hvplot.explorer()` as an alternate entry point to create an explorer ([#1154](https://github.com/holoviz/hvplot/pull/1154))
- Add the `resample_when` option to dynamically enable datashade/rasterize/downsample ([#1103](https://github.com/holoviz/hvplot/pull/1103))
- Expose the HoloViews timeseries downsampling algorithm (LTTB) with the `downsample` option ([#1127](https://github.com/holoviz/hvplot/pull/1127), [#1157](https://github.com/holoviz/hvplot/pull/1157))
- Expose the HoloViews `autorange` option ([#1128](https://github.com/holoviz/hvplot/pull/1128), [#1158](https://github.com/holoviz/hvplot/pull/1158), [#1174](https://github.com/holoviz/hvplot/pull/1174))
- Allow string formatting for *labels* plots ([#1140](https://github.com/holoviz/hvplot/pull/1140))
- Support plots that use `by` with `rasterize` with HoloViews `ImageStack` ([#1132](https://github.com/holoviz/hvplot/pull/1132), [#1144](https://github.com/holoviz/hvplot/pull/1144))
- Update `show` to return the configured Server or StoppableThread ([#1121](https://github.com/holoviz/hvplot/pull/1121))

Bug fixes:

- Do not force `geo=True` if tiles are provided ([#1083](https://github.com/holoviz/hvplot/pull/1083), [#1113](https://github.com/holoviz/hvplot/pull/1113))
- Fix x-limit, y-limit, and rasterize support for geo features  ([#1135](https://github.com/holoviz/hvplot/pull/1135), [#1163](https://github.com/holoviz/hvplot/pull/1163))
- Fix handling WKT strings and add `pyproj.CRS` support ([#1092](https://github.com/holoviz/hvplot/pull/1092), [#1139](https://github.com/holoviz/hvplot/pull/1139))
- Underlay land and ocean features ([#1151](https://github.com/holoviz/hvplot/pull/1151))
- Fix `.hist` for the Ibis data source ([#997](https://github.com/holoviz/hvplot/pull/997))
- No longer suggest installing datashader and geoviews from the `pyviz` channel ([#1130](https://github.com/holoviz/hvplot/pull/1130))
- Silence GDAL exceptions warning ([#1142](https://github.com/holoviz/hvplot/pull/1142))

Documentation:

- Various docs improvements and addition of an *Integrations* guide ([#1084](https://github.com/holoviz/hvplot/pull/1084), [#1173](https://github.com/holoviz/hvplot/pull/1173), [#1177](https://github.com/holoviz/hvplot/pull/1177))
- Extending the reference gallery ([#999](https://github.com/holoviz/hvplot/pull/999))
- Added extra `size` parameter to scatter plot example ([#1118](https://github.com/holoviz/hvplot/pull/1118))

Compatibility:

- Preparations before the release of Param 2.0 ([#1146](https://github.com/holoviz/hvplot/pull/1146), [#1164](https://github.com/holoviz/hvplot/pull/1164))
- Pin `Param` to `<3.0` ([#1175](https://github.com/holoviz/hvplot/pull/1175))
- Drop Python 3.6 and 3.7 ([#1077](https://github.com/holoviz/hvplot/pull/1077))

Infrastructure / Tests:

- Add Dask DataFrame plot test ([#1131](https://github.com/holoviz/hvplot/pull/1131))
- Add codespell to pre-commit ([#1172](https://github.com/holoviz/hvplot/pull/1172))
- Add OpenCollective sponsor link on the repo page ([#1123](https://github.com/holoviz/hvplot/pull/1123))


[Full changelog](https://github.com/holoviz/hvplot/compare/v0.8.4...v0.9.0)


## Version 0.8.4 (2023-06-05)

The 0.8.4 release brings a number of bugfixes and documentation improvements. Many thanks to @kthyng (first contribution!), @raybellwaves, @jsignell , @Hoxbro, @maximlt and  @philippjfr for contributing.

Bug fixes:

* Fix `.interactive` layout compatibility with Bokeh 3 ([1076](https://github.com/holoviz/hvplot/pull/1076))
* Fix usage with intake ([1052](https://github.com/holoviz/hvplot/pull/1052))
* Fix deprecated usage of Param 2.0 ([1064](https://github.com/holoviz/hvplot/pull/1064))
* Fix projection when `xlim`/`ylim` provided ([1053](https://github.com/holoviz/hvplot/pull/1053))
* Fix interpretation of positional arg with geopandas, now used as `color` ([1056](https://github.com/holoviz/hvplot/pull/1056))
* Fix import error messages for geo dependencies ([1054](https://github.com/holoviz/hvplot/pull/1054))
* Fix usage of `hover` for geometries - make it less likely to fail ([1055](https://github.com/holoviz/hvplot/pull/1055))

Documentation:

* Update to latest nbsite & pydata-sphinx-theme ([1070](https://github.com/holoviz/hvplot/pull/1070))
* Update to Google Analytics4 ([1075](https://github.com/holoviz/hvplot/pull/1075))

Maintenance:

* Add ipywidgets to the examples deps ([1048](https://github.com/holoviz/hvplot/pull/1048))

## Version 0.8.3 (2023-03-17)

The 0.8.3 release brings a number of bugfixes and documentation improvements. This release is also marked by the adoption of a formal project governance, ensuring hvPlot's future as a healthy open-source project! Many thanks to @raybellwaves, @jsignell (welcome back!), @droumis, @Hoxbro, @maximlt, @philippjfr and @MarcSkovMadsen for contributing!

Please note that hvPlot is not yet compatible with Bokeh 3.

Bug fixes:

* Allow `.hvplot` to execute for the *ibis* backend ([#990](https://github.com/holoviz/hvplot/pull/990))
* Improve package name in error message ([#1005](https://github.com/holoviz/hvplot/pull/1005))
* Let ``process_crs`` try a few approaches before raising error ([#1026](https://github.com/holoviz/hvplot/pull/1026))
* Fix `label` on unnamed data array ([#1025](https://github.com/holoviz/hvplot/pull/1025))
* Only use xarray `long_name` metadata if it is a string ([#1031](https://github.com/holoviz/hvplot/pull/1031))
* Replace deprecated Param methods ([#1030](https://github.com/holoviz/hvplot/pull/1030))
* Ensure interactive pipeline is not re-executed needlessly ([#1029](https://github.com/holoviz/hvplot/pull/1029))
* Fixes `subplots=True` for `geo=True` and `by` ([#761](https://github.com/holoviz/hvplot/pull/761))
* Force column names to string ([#1042](https://github.com/holoviz/hvplot/pull/1042))

Documentation:

* Docstring fixes ([#985](https://github.com/holoviz/hvplot/pull/985))
* Improve the `hist` reference guide ([#1002](https://github.com/holoviz/hvplot/pull/1002))
* Improve the `bar` reference guide ([#1032](https://github.com/holoviz/hvplot/pull/1032))

Project governance:

* Create initial project gov docs ([#1016](https://github.com/holoviz/hvplot/pull/1016))

Maintenance:

* Rename *master* branch to *main* ([#1011](https://github.com/holoviz/hvplot/pull/1011))
* Add Python 3.11 to the test matrix ([#1015](https://github.com/holoviz/hvplot/pull/1015))
* Run examples with `nbval` instead of `nbsmoke` ([#1044](https://github.com/holoviz/hvplot/pull/1044))
* Fix the build by better defining the package extras ([#1046](https://github.com/holoviz/hvplot/pull/1046))

## Version 0.8.2 (2022-11-24)

The 0.8.2 release brings a number of bugfixes and documentation improvements. @MarcSkovMadsen has kept improving the docstrings and we congratulate @sophiamyang for her first contribution that made the landing page nicer! Many thanks to @droumis, @Hoxbro, @maximlt, @philippjfr and @MarcSkovMadsen for contributing!

Please note that hvPlot is not yet compatible with Bokeh 3.

- Dependencies:
  - Add Panel lower pin to ensure Bokeh 3 is not installed ([#974](https://github.com/holoviz/hvplot/pull/974))
- Interactive:
  - Support slice ([#776](https://github.com/holoviz/hvplot/pull/776))
- Plot:
  - Convert `DataFrame` columns with type `RangeIndex` to strings to ensure compatibility with `HoloViews` ([#932](https://github.com/holoviz/hvplot/pull/932))
  - Ensure that `xarray` dataset metadata propagates to `NdOverlays` ([#930](https://github.com/holoviz/hvplot/pull/930))
  - Support `rioxarray` ([#905](https://github.com/holoviz/hvplot/pull/905))
  - Improve error message mentioning `pyproj` ([#950](https://github.com/holoviz/hvplot/pull/950))
- Explorer:
  - Don't error on datetime-like axis ([#968](https://github.com/holoviz/hvplot/pull/968))
  - Don't use xlim/ylim slider if start and end values are identical ([#966](https://github.com/holoviz/hvplot/pull/966))
- Documentation:
  - New and updated docstrings ([#892](https://github.com/holoviz/hvplot/pull/892), [#863](https://github.com/holoviz/hvplot/pull/863))
  - Improve the landing page ([#874](https://github.com/holoviz/hvplot/pull/874), [#903](https://github.com/holoviz/hvplot/pull/903), [#876](https://github.com/holoviz/hvplot/pull/876))
  - Change *http* to *https* ([#873](https://github.com/holoviz/hvplot/pull/873))
  - Add intended `rolling_window` param into pipeline ([#944](https://github.com/holoviz/hvplot/pull/944))
  - Updates the README ([#817](https://github.com/holoviz/hvplot/pull/817))
  - Miscellaneous documentation improvements ([#866](https://github.com/holoviz/hvplot/pull/866), [#887](https://github.com/holoviz/hvplot/pull/887), [#910](https://github.com/holoviz/hvplot/pull/910))
- Development:
  - Add `pre-commit` to format and lint the code on commits ([#967](https://github.com/holoviz/hvplot/pull/967))
- CI:
  - Miscellaneous fixes and improvements ([#867](https://github.com/holoviz/hvplot/pull/867), [#922](https://github.com/holoviz/hvplot/pull/922), [#947](https://github.com/holoviz/hvplot/pull/947), [#948](https://github.com/holoviz/hvplot/pull/948), [#949](https://github.com/holoviz/hvplot/pull/949), [#960](https://github.com/holoviz/hvplot/pull/960), [#977](https://github.com/holoviz/hvplot/pull/977))

## Version 0.8.1 (2022-08-26)

The 0.8.1 release is a bug fix release, focusing mostly on improving `.interactive` and the *explorer*. The documentation has seen some improvements too; @MarcSkovMadsen has been improving the docstrings so make sure to check them out.  Many thanks to @jlstevens, @Hoxbro, @maximlt, @philippjfr and @MarcSkovMadsen for contributing!

- Interactive:
  - Set interactive function to lazy to avoid calling it twice ([#772](https://github.com/holoviz/hvplot/pull/772))
  - Add support for hvplot kind accessor ([#781](https://github.com/holoviz/hvplot/pull/781), [#858](https://github.com/holoviz/hvplot/pull/858))
  - Add more tests to `Interactive` and some comments ([#812](https://github.com/holoviz/hvplot/pull/812))
  - Fixes to the operators implemented by Interactive ([#814](https://github.com/holoviz/hvplot/pull/814))
  - Propagate `max_rows` ([#815](https://github.com/holoviz/hvplot/pull/815))
  - Only register the function parameters watchers once ([#818](https://github.com/holoviz/hvplot/pull/818))
  - Do not re-execute transform on copied clones ([#833](https://github.com/holoviz/hvplot/pull/833))
  - Internal callback made dependent only when parameters are found ([#857](https://github.com/holoviz/hvplot/pull/857))
- Explorer:
  - Make the explorer easier to use ([#799](https://github.com/holoviz/hvplot/pull/799))
  - Enhancement to Fields tab in explorer ([#811](https://github.com/holoviz/hvplot/pull/811))
  - Remove the marker styling option of the explorer ([#809](https://github.com/holoviz/hvplot/pull/809))
- Plot:
  - Make `rescale_discrete_levels` a plot option ([#758](https://github.com/holoviz/hvplot/pull/758))
  - Ensure that dataframes with multiple columns are categorically shaded ([#759](https://github.com/holoviz/hvplot/pull/759))
  - Display a color bar when rasterize is enabled ([#782](https://github.com/holoviz/hvplot/pull/782))
  - Update the expected DataSet plot title after xarray `2022.6.0` ([#795](https://github.com/holoviz/hvplot/pull/795))
  - Set categorically shaded when there's more than one variable ([#843](https://github.com/holoviz/hvplot/pull/843))
  - Clone GeoViews' features ([#850](https://github.com/holoviz/hvplot/pull/850))
- Documentation:
  - Add new and improve existing docstrings ([#793](https://github.com/holoviz/hvplot/pull/793), [#826](https://github.com/holoviz/hvplot/pull/826), [#827](https://github.com/holoviz/hvplot/pull/827), [#822](https://github.com/holoviz/hvplot/pull/822))
  - Update developer install instructions ([#794](https://github.com/holoviz/hvplot/pull/794))
  - Rework the landing page and add a Getting started guide ([#838](https://github.com/holoviz/hvplot/pull/838))
- Misc:
  - No longer use basestring from holoviews.core.util ([#757](https://github.com/holoviz/hvplot/pull/757))
  - Ensure that repr is initialized on hvplot backend import ([#774](https://github.com/holoviz/hvplot/pull/774))
  - Add RGB test data ([#779](https://github.com/holoviz/hvplot/pull/779))
  - Add flatten utility function ([#798](https://github.com/holoviz/hvplot/pull/798))

## Version 0.8.0 (2022-05-09)

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

## Version 0.7.3 (2021-07-23)

This is a minor release focusing on greatly improving the
[`.interactive()`](https://hvplot.holoviz.org/user_guide/Interactive.html)
API for flexibly building simple apps using widget controls. Thanks to
@jbednar and @jlstevens for a few small fixes and many thanks to
@philippjfr for all the rest!

Features:

- Improved `.interactive` Dataframe support: max_rows display, column
  access ([#640](https://github.com/holoviz/hvplot/pull/640))
- Improved accessor and attribute behavior for `.interactive`
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

## Version 0.7.2 (2021-05-22)

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

## Version 0.7.1 (2021-03-03)

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

## Version 0.7.0 (2020-11-18)

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

## Version 0.6.0 (2020-06-02)

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

## Version 0.5.2 (2019-10-17)

This release mostly includes contributions from @jsignell.

- Allow tile sources to be objects as well as strings ([#345](https://github.com/holoviz/hvplot/pull/345))
- Set ``geo=True`` by default for coastline ([#344](https://github.com/holoviz/hvplot/pull/344))
- Add ``check_symmetric_max`` limit for working with large data ([#340](https://github.com/holoviz/hvplot/pull/340))
- Expose plot at top level, to support `pd.options.plotting.backend = 'hvplot'` ([#347](https://github.com/holoviz/hvplot/pull/347))
- Misc bug fixes ([#341](https://github.com/holoviz/hvplot/pull/341), [#343](https://github.com/holoviz/hvplot/pull/343), [#346](https://github.com/holoviz/hvplot/pull/346))

## Version 0.5.1 (2019-10-13)

Minor release with updates to continuous integration setup (from @jsignell).

## Version 0.5.0 (2019-10-10)

**October 10, 2019**

This is a major release that includes bug fixes, changes to default behavior, and enhancements.

Features:
 - Widget handling capabilities to facilitate interactivity ([#323](https://github.com/holoviz/hvplot/pull/323), [#331](https://github.com/holoviz/hvplot/pull/331))
 - New default colormaps ([#258](https://github.com/holoviz/hvplot/pull/258), [#316](https://github.com/holoviz/hvplot/pull/316), [#206](https://github.com/holoviz/hvplot/pull/206))
 - long_name(units) used to label xarray objects ([#173](https://github.com/holoviz/hvplot/pull/173))
 - Derived datetime accessor handlind ([#263](https://github.com/holoviz/hvplot/pull/263), [#286](https://github.com/holoviz/hvplot/pull/286))
 - `coastline` and `tiles` options for easy geo plots.
 - Automatic date sorting ([#259](https://github.com/holoviz/hvplot/pull/259))
 - Allow use of strings as aggregators for datashader ([#257](https://github.com/holoviz/hvplot/pull/257))

## Version 0.4.0 (2019-01-28)

This is a major release which includes the addition of a networkx
plotting API and a number of important bug fixes.

Features:

- A new NetworkX interface providing equivalents for the networkx plotting module ([#152](https://github.com/holoviz/hvplot/pull/152), [#154](https://github.com/holoviz/hvplot/pull/154))

Fixes:

- Fixed handling of labelled property to hide axis labels ([#142](https://github.com/holoviz/hvplot/pull/142))
- Fixed handling of DataArrays and groupby on RGB plots ([#138](https://github.com/holoviz/hvplot/pull/138), [#141](https://github.com/holoviz/hvplot/pull/141))
- Allow setting axis position ([#149](https://github.com/holoviz/hvplot/pull/149))
- Fixes for setting the axis positions ([#145](https://github.com/holoviz/hvplot/pull/145))

## Version 0.3.0  (2019-01-07)

This release includes a number of major improvements to the documentation and core functionality as well as a variety of bug fixes.

- Added improved docstrings including all available options ([#103](https://github.com/pyviz/hvplot/pull/103), [#134](https://github.com/pyviz/hvplot/pull/134))
- Added support for tab-completion in interactive environments such as IPython and Jupyter notebooks ([#134](https://github.com/pyviz/hvplot/pull/134))
- Added support for ``rgb`` ([#137](https://github.com/pyviz/hvplot/pull/137)) and ``labels`` ([#98](https://github.com/pyviz/hvplot/pull/98)) plot types
- Exposed bokeh styling options for all plot types ([#134](https://github.com/pyviz/hvplot/pull/134))
- Compatibility with latest HoloViews/GeoViews releases ([#113](https://github.com/pyviz/hvplot/pull/113), [#118](https://github.com/pyviz/hvplot/pull/118), [#134](https://github.com/pyviz/hvplot/pull/134))
- Added control over tools ([#120](https://github.com/pyviz/hvplot/pull/120)) and legend position ([#119](https://github.com/pyviz/hvplot/pull/119))

## Previous versions

Versions 0.1.1, 0.2.0, 0.2.1 were released on the 6th of July 2018, 7th of July 2018 and 8th of July 2018.
