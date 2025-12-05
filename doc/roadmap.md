# Roadmap

## hvPlot 1.0
To be released in 2026.

### 1. Documentation

In 2025, we obtained a Small Development Grant from NumFocus that allowed us to significantly update the documentation, adding a new Reference section with a description of all the plotting options and an automated API reference, a new examples gallery, and new tutorials.

To complete this documentation update, we need now to convert the user guides into How-To guides, Tutorials, and Explanation pages.

### 2. Refactor the test suite

The test suite should be re-factored and improved to catch bugs before users have to report them and to prevent potential regressions.

### 3. Add donut and pie charts

There are many references in the literature that argue that pie charts don't communicate data precisely enough (humans judge length better than angle, so it’s difficult to compare slices accurately). For this reason, pie charts haven't been added to HoloViews which instead recommends using bar charts. Yet, pie charts are very commonly used and not offering this option in hvPlot is a big gap we aim to fill by adding a Donut plot type in HoloViews, and a `donut` and a `pie` method to hvPlot.

### 4. Native support for more dataframe libraries like Polars

HoloViews [added support](https://github.com/holoviz/holoviews/pull/6567) in version 1.22.0 for [Narwhals](https://narwhals-dev.github.io/narwhals/) as a data backend. Narwhals is a library that provides a unified interface to many dataframe libraries (its own API being heavily inspired by Polars). hvPlot already provides good support for various dataframe libraries, like Pandas and Dask, when these libraries have a data backend implemented in HoloViews. When they don't, which is/was the case for Polars for example, hvPlot first casts the user dataframe to a supported type (Pandas typically). With the new Narwhals backend in HoloViews, it is now possible for hvPlot to avoid casting upfront user dataframes, and instead pass them down to HoloViews, which can handle them with Narwhals.

## Post hvPlot 1.0

### 1. Bug fixes

hvPlot provides already many (many!) features to its users. However, it also has many bugs that prevent its adoption.

1. hvPlot's development should favor bug fixes vs. new features or feature enhancements.
2. Bugs reported by hvPlot users regularly come from one of its dependencies, typically HoloViews. It should be made easy for hvPlot users to find these bugs on GitHub. These bugs should be fixed too.

### 2. Figure out the future of the `.interactive` API

Param 2.0 added a new API for [reactive expressions](https://param.holoviz.org/user_guide/Reactive_Expressions.html), allowing Param users and users of libraries leveraging this feature (like Panel) to write purely reactive code. Reactive expressions are in fact a generalized and improved re-implementation of `.interactive()` from hvPlot.

1. hvPlot should determine whether the `.interactive` API even still has its place in the project.
2. If so, its implementation should be updated to use Param's implementation. If not, the feature should be deprecated.

## 3. Expose features from HoloViews

While the focus of hvPlot's development should be to shoot for stability, an easy way (usually) to add features to hvPlot is to expose new features added to HoloViews. For instance, hvPlot could add support for [dual-axis plots](https://holoviews.org/user_guide/Customizing_Plots.html#supported-multi-y-options), a feature added to HoloViews in 2023. This is a good way for the HoloViz ecosystem to expose more of its new features, that sometimes end up being somewhat hidden in the documentation of HoloViews.

1. hvPlot should track with *enhancement feature* issues the new features added to HoloViews and adapted to the project.
2. Features that are easy to implement, test, and document should be implemented.

## 4. Improve the Explorer

The Explorer, still in the development phase, needs to be improved in various ways.

1. hvPlot should draw inspiration from other similar components (e.g. Tableau, Excel, Superset) for guiding its design and user experience.
2. The Explorer should work well with all the data types supported by hvPlot.
3. The Explorer should be better integrated into the documentation, both as a tool to explore hvPlot's API and to explore data.

## 5. Increase hvPlot's presence within PyData

hvPlot is a library that integrates with many data libraries of the PyData ecosystem and should ideally be more exposed in the documentation of these libraries.

1. Issues/Discussions should be opened with the maintainers of these libraries to gauge how interested they would be in exposing more hvPlot.
2. For the interested libraries, updates to their documentation should be made, with support provided to the maintainers over time.
