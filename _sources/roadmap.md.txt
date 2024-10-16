# Roadmap

This page includes an ambitious roadmap for hvPlot for 2024.

## 1. Documentation, documentation, documentation

### Context

hvPlot's website currently has the following structure:

- A landing page describing its main features.
- A *Getting Started* guide (recently added) that is a short tutorial demonstrating its basic capabilities.
- Many *User Guides*, focusing on a domain (e.g. *Geographic Data*), on a data type (*Gridded Data*), on a feature (e.g. *Interactive*), or on a specific part of the API (e.g. *Customization*).
- A *Reference Gallery* with a page per plot method (actually incomplete), separated by these categories: Pandas, GeoPandas, and Xarray. Each reference page is usually short, only uses Bokeh, and doesn't include the whole API applicable to the plot method.
- A *Topics* short page containing a few links to other websites using hvPlot
- A *Developer Guide*, a *Releases* page and an *About* page

hvPlot users have repeatedly complained about the quality of its documentation, which seems to mostly stem from:

- The API is not being documented.
- The API is not being enough demonstrated in a single place; users have to assemble examples from different pages.
- An implicit reliance on HoloViews' documentation (e.g. for the options) that itself isn't in great shape.
- The difficulty to run locally all or parts of the documentation (that relies on somewhat complex datasets and many libraries).

### Goals

The main priority of the hvPlot project should be to improve its documentation. Some of the guiding principles of the documentation update should be:

- To adopt the [Diataxis framework](https://diataxis.fr). [Panel](https://panel.holoviz.org/) recently overhauled part of its documentation, dividing the documentation into tutorials, how-to guides, explanations, and references. Note however that the experience from Panel revealed that changes need to happen gradually and that existing documentation should be removed when newer documentation is in place.
- The code on the website should be easy to execute locally, using simple datasets to fetch and not relying on special libraries.

1. The most important focus should be on the *Reference*:
    - The API should be fully and automatically documented, see for example how [Plotly](https://plotly.com/python-api-reference/generated/plotly.express.line) and [Pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html) document their `line` function.
    - The plot methods should be documented with many more examples, Plotly again does this in a great way, collecting on a [single page many examples](https://plotly.com/python/line-charts/) which allow the user to quickly find. These examples should be automatically built for the three supported plotting backends (Bokeh, Matplotlib, Plotly).
    - The style options should all be documented automatically, for each plotting backend.
2. hvPlot users very often come from another library (Pandas, GeoPandas, Xarray, Polars, etc.), and the documentation should guide them better and help them to migrate:
    - Dedicated entry points should be created for these users, in the form of tutorials.
    - The landing page should point them to these tutorials.
3. An advanced plotting tutorial should be created, which users would follow once they have completed the Getting Started and/or Migration tutorials, to deepen their understanding of hvPlot.
4. hvPlot is not just a plotting library, it is a platform for advanced data analysis through visualization. Some of the more advanced concepts, such as the processing done by Datashader, should be explained in a new top-level *Explanation* section.
5. The previous tasks should often need to reuse content from the *User Guides*. Once they are completed it should appear more clearly how to re-structure them.

## 2. Streamline the developer experience

hvPlot, and the HoloViz projects in general, do not make it very easy for its potential contributors to set up a development environment and contribute.

1. hvPlot should no longer use [pyctdev](https://github.com/holoviz-dev/pyctdev) and instead adopt a more common framework (e.g. hatch, pdm, poetry, tox)
2. The *Developer Guide* should be adapted accordingly.

## 3. Bug fixes

hvPlot provides already many (many!) features to its users. However, it also has many bugs that prevent its adoption.

1. hvPlot's development should favor bug fixes vs. new features or feature enhancements.
2. hvPlot's test suite should be re-factored and improved to catch bugs before users have to report them and to prevent potential regressions.
3. Bugs reported by hvPlot users regularly come from one of its dependencies, typically HoloViews. It should be made easy for hvPlot users to find these bugs on GitHub. These bugs should be fixed too.

## 4. Figure out the future of the `.interactive` API

Param 2.0 added a new API for [reactive expressions](https://param.holoviz.org/user_guide/Reactive_Expressions.html), allowing Param users and users of libraries leveraging this feature (like Panel) to write purely reactive code. Reactive expressions are in fact a generalized and improved re-implementation of `.interactive()` from hvPlot.

1. hvPlot should determine whether the `.interactive` API even still has its place in the project.
2. If so, its implementation should be updated to use Param's implementation. If not, the feature should be deprecated.

## 5. Expose features from HoloViews

While the focus of hvPlot's development should be to shoot for stability, an easy way (usually) to add features to hvPlot is to expose new features added to HoloViews. For instance, hvPlot could add support for [dual-axis plots](https://holoviews.org/user_guide/Customizing_Plots.html#supported-multi-y-options), a feature added to HoloViews in 2023. This is a good way for the HoloViz ecosystem to expose more of its new features, that sometimes end up being somewhat hidden in the documentation of HoloViews.

1. hvPlot should track with *enhancement feature* issues the new features added to HoloViews and adapted to the project.
2. Features that are easy to implement, test, and document should be implemented.

## 6. Improve the Explorer

The Explorer, still in the development phase, needs to be improved in various ways.

1. hvPlot should draw inspiration from other similar components (e.g. Tableau, Excel, Superset) for guiding its design and user experience.
2. The Explorer should work well with all the data types supported by hvPlot.
3. The Explorer should be better integrated into the documentation, both as a tool to explore hvPlot's API and to explore data.

## 7. Increase hvPlot's presence within PyData

hvPlot is a library that integrates with many data libraries of the PyData ecosystem and should ideally be more exposed in the documentation of these libraries.

1. Issues/Discussions should be opened with the maintainers of these libraries to gauge how interested they would be in exposing more hvPlot.
2. For the interested libraries, updates to their documentation should be made, with support provided to the maintainers over time.

## 8. Prepare for hvPlot `1.0` in 2025

hvPlot was released in 2018 and has gained a decent level of adoption since then with about 270,000 downloads per month (aggregating downloads from [PyPI and Anaconda.org](https://pyviz.org/tools.html#high-level-shared-api)). Its API has been lately stable and there is no major change coming up. Releasing hvPlot `1.0` in 2025 would be a good signal to its current and future users, in particular, if in 2024 a focus is made on improving its documentation and reducing its number of bugs.

1. Potential major API changes that can only happen in a *major* release should be discussed this year.
2. Potential deprecations should be implemented this year.
