# Roadmap

hvPlot was released in 2018 and has gained many features since then, becoming a super-charged version of Pandas `.plot()` API, with support for many data structures of the PyData ecosystem (Pandas, Dask, Xarray, GeoPandas, etc.), for multiple plotting backends, and for many powerful features (plotting large datasets with Datashader, geographic data with GeoViews, plotting streaming data, etc.). Despite this, hvPlot isn't currently as widely known as some of the alternatives and has huge room to grow.

## hvPlot development principles

The following principles are derived from the goal of improving hvPlot's stability and user-friendliness.

1. Reliability first

Prioritize reducing bugs over introducing new features. New features and enhancements are welcome, but only when they do not compromise overall stability. Bugs originating in hvPlot's dependencies, particularly HoloViews, should be easy for users to discover, track, and see resolved through clear GitHub issues and coordinated fixes.

2. Documentation as a core feature

Treat documentation as a first-class part of the project. Continuously improve clarity, coverage, and examples, such as by expanding the gallery, until the documentation meets or exceeds the quality of comparable libraries (e.g. Altair, Plotly Express, plotnine). Ensure documentation remains accurate and up to date as the codebase evolves.

3. Strong, accessible testing

Maintain a test suite that meaningfully catches regressions and common user errors. Make writing and extending tests straightforward so that contributors can easily add coverage alongside bug fixes and new functionality.

4. User-centered developer experience

Improve the day-to-day experience of using hvPlot by adding type hints to support IDE tooling and by providing clearer, more actionable error messages when things go wrong.

5. Deep integration with the PyData ecosystem

Actively increase hvPlot’s visibility and adoption across the PyData ecosystem. Engage maintainers of related libraries through issues and discussions to explore deeper integration or exposure of hvPlot, and support those efforts with documentation updates and ongoing collaboration.

6. Thoughtful feature completeness

Expose stable, relevant HoloViews capabilities through hvPlot when they add clear user value (e.g. dual axes, native Polars support). Identify and implement essential plotting features expected of a general-purpose plotting library when they are missing (e.g. pie charts), while maintaining hvPlot's simplicity and reliability.

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
