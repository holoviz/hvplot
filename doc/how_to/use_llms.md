# Using hvPlot with an AI assistant

AI assistants (like Claude, GitHub Copilot, or OpenAI Codex) can write hvPlot code much more reliably when they have access to up-to-date, structured documentation instead of guessing from stale training data. This guide shows you how to give your assistant that context, either by pointing it at hvPlot's generated `llms.txt` and Markdown docs, or by installing the HoloViz Agent Skills.

## What you'll accomplish

By the end of this guide you'll be able to:

- Install the HoloViz skills so your assistant follows hvPlot best practices automatically
- Give your AI assistant a curated index of the most useful hvPlot documentation pages

## Prerequisites

- A python package installer like `pip` or `uv` if you want to install the skills
- An AI assistant that can read web content or local files (for example Claude, GitHub Copilot, or OpenAI Codex)

## Install the HoloViz skills

The [holoviz-skills](https://holoviz-dev.github.io/holoviz-skills/) repository provides a curated collection of [Agent Skills](https://www.anthropic.com/news/skills) for the HoloViz ecosystem, including hvPlot. Agent Skills are folders of instructions and references that teach an assistant how to work with a library correctly.

::::{tab-set}

:::{tab-item} uv

```bash
uvx holoviz-skills@latest install
```

:::

:::{tab-item} pip
```bash
pip install holoviz-skills
```

:::

::::

```bash
holoviz-skills install
```

The `install` command auto-detects the AI tools on your machine. You can also target a specific tool, for example:

```bash
holoviz-skills install --claude-code
holoviz-skills install --copilot
```

You may need to restart your assistant so it picks up the newly installed skills.

## Point your assistant at the docs

hvPlot publishes a machine-friendly index of its documentation that your assistant can fetch directly.

1. Tell your assistant to fetch the index:

   `https://hvplot.holoviz.org/en/docs/latest/llms.txt`

2. The index lists the most relevant pages and links to their Markdown versions under:

   `https://hvplot.holoviz.org/en/docs/latest/markdown/`, for example, `https://hvplot.holoviz.org/en/docs/latest/markdown/tutorials/getting_started.md`

3. Ask your assistant to read the pages relevant to your task before writing code. For example, to create a plot you might have it read the Getting Started tutorial and the API reference page for the method you need. On its own, it will read the appropriate Markdown pages.

The Markdown pages are intentionally free of the navigation chrome, CSS, and JavaScript of the full HTML site, so they consume far fewer tokens and are easier for an assistant to parse.

## Which approach should I use?

- **Point your assistant at the docs** is a good fit for a one-off task or when you can't install packages, and it always reflects the latest published docs.
- **Install the HoloViz skills** gives your assistant packaged, opinionated guidance that works offline, but you need to update it as hvPlot evolves. Once the skills are installed, pointing to the Markdown docs should no longer be needed if you want your agent to be able to fetch the latest docs, as the skills already teach the agent how to do that.
