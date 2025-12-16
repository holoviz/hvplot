# Roadmap

hvPlot was released in 2018 and has gained many features since then, becoming a super-charged version of Pandas `.plot()` API, with support for many data structures of the PyData ecosystem (Pandas, Dask, Xarray, GeoPandas, etc.), for multiple plotting backends, and for many powerful features (plotting large datasets with Datashader, geographic data with GeoViews, plotting streaming data, etc.). Yet, it hasn't been adopted as much as we hoped.

Instead of focusing on new features, the strategy we propose to follow in this roadmap is based on stability and user-friendliness, we want hvPlot's features to shine!

- More bug fixes:
    - hvPlot's development should favor bug fixes over new features or feature enhancements. Of course, we do not intend to prevent new features or enhancements; we are simply aiming to reduce the number of bugs rather than increase it.
    - Bugs reported by hvPlot users regularly originate from one of its dependencies, typically HoloViews. It should be easy for hvPlot users to find these bugs on GitHub, and those issues should be fixed as well.
- Better documentation:
    - The documentation should continuously be improved (e.g. by extending the gallery) until it reaches a level that is at least as good as hvPlot's alternatives (e.g. Altair, Plotly Express, plotnine).
    - The documentation should be kept up to date.
- Higher test coverage:
    - The test suite should catch more bugs.
    - It should be easier for a contributor to add tests.
- Improved user experience:
    - Type hints should be added to the codebase to enhance the experience of users working from an IDE.
    - Error messages should be improved to better guide users when things go wrong.
- Increase hvPlot's presence within PyData
    - Issues or discussions should be opened with the maintainers of these libraries to gauge how interested they would be in integrating or exposing more of hvPlot.
    - For interested libraries, updates to their documentation should be made, with support provided to the maintainers over time.
- Add missing features:
    - HoloViews features that are stable enough and relevant for hvPlot's users (e.g. dual axis, native Polars support) should be exposed in hvPlot.
    - Important features a plotting library like hvPlot is missing should be identified and added (e.g. pie charts)

Based on these principles, we aim to release 1.0 in early 2026, signaling to hvPlot's user base that it is a stable project already for a few years.

## hvPlot 1.0

### 1. Documentation

In 2025, we obtained a Small Development Grant from NumFocus that allowed us to significantly update the documentation, adding a new Reference section with a description of all plotting options and an automated API reference, a new examples gallery, and new tutorials.

To complete this documentation update, we now need to convert the user guides into How-To guides, Tutorials, and Explanation pages.

### 2. Refactor the test suite

The test suite should be refactored and improved to catch bugs before users have to report them and to prevent potential regressions.

### 3. Add donut and pie charts

There are many references in the literature that argue that pie charts do not communicate data precisely enough (humans judge length better than angle, so it’s difficult to compare slices accurately). For this reason, pie charts have not been added to HoloViews, which instead recommends bar charts. Yet pie charts are very commonly used, and not offering this option in hvPlot is a significant gap we aim to fill by adding a Donut plot type in HoloViews and `donut` and `pie` methods to hvPlot.

### 4. Native support for more dataframe libraries like Polars

HoloViews added support in version 1.22.0 for Narwhals as a data backend. Narwhals is a library that provides a unified interface to many DataFrame libraries (its API being heavily inspired by Polars). hvPlot already provides good support for various DataFrame libraries, like Pandas and Dask, when these libraries have a data backend implemented in HoloViews. When they do not — as was the case for Polars, for example — hvPlot previously cast the user's DataFrame to a supported type (usually Pandas). With HoloViews' Narwhals backend, hvPlot can now avoid upfront casting and pass DataFrames directly to HoloViews, which can handle them via Narwhals.

## Post hvPlot 1.0

### 1. Figure out the future of the `.interactive` API

Param 2.0 introduced a new API for reactive expressions, allowing Param users and users of libraries leveraging this feature (like Panel) to write purely reactive code. Reactive expressions are, in fact, a generalized and improved re-implementation of `.interactive()` from hvPlot.

1. hvPlot should determine whether the `.interactive()` API still has a place in the project.
2. If so, its implementation should be updated to use Param's implementation. If not, the feature should be deprecated.

## 2. Improve the Explorer

The Explorer is still in development and needs improvements in several areas.

1. The Explorer's design and user experience should draw inspiration from other similar components (e.g. Tableau, Excel, Superset).
2. The Explorer should work well with all the data types supported by hvPlot.
3. The Explorer should be better integrated into the documentation, both as a tool to explore hvPlot's API and to explore data.
