# Using hvPlot with an AI assistant

AI assistants (like Claude, GitHub Copilot, or OpenAI Codex) can write hvPlot code much more reliably when they have access to up-to-date, structured documentation instead of guessing from stale training data. This guide shows you how to give your assistant that context, either by pointing it at hvPlot's generated `llms.txt` and Markdown docs, or by installing the HoloViz Agent Skills.

## What you'll accomplish

By the end of this guide you'll be able to:

- Give your AI assistant a curated index of the most useful hvPlot documentation pages
- Install the HoloViz skills so your assistant follows hvPlot best practices automatically

## Prerequisites

- An AI assistant that can read web content or local files (for example Claude, GitHub Copilot, or OpenAI Codex)
- [Python](https://www.python.org/) 3.12+ and `pip` if you want to install the skills

## Point your assistant at the docs

hvPlot publishes a machine-friendly index of its documentation that your assistant can fetch directly.

1. Tell your assistant to fetch the index:

   `https://hvplot.holoviz.org/en/docs/latest/llms.txt`

2. The index lists the most relevant pages and links to their Markdown versions under:

   `https://hvplot.holoviz.org/en/docs/latest/markdown/`

3. Ask your assistant to read the pages relevant to your task before writing code. For example, to create a plot you might have it read `tutorials/getting_started.md` and the API reference page for the method you need.

The Markdown pages are intentionally free of the navigation chrome, CSS, and JavaScript of the full HTML site, so they consume far fewer tokens and are easier for an assistant to parse.

## Install the HoloViz skills

The [holoviz-skills](https://holoviz-dev.github.io/holoviz-skills/) repository provides a curated collection of [Agent Skills](https://www.anthropic.com/news/skills) for the HoloViz ecosystem, including hvPlot. Agent Skills are folders of instructions and references that teach an assistant how to work with a library correctly.

1. Install the package:

   ```bash
   pip install holoviz-skills
   ```

2. Install the skills for your tool:

   ```bash
   holoviz-skills install
   ```

   This auto-detects the AI tools on your machine. You can also target a specific tool, for example:

   ```bash
   holoviz-skills install --claude-code
   holoviz-skills install --copilot
   ```

3. Restart your assistant so it picks up the newly installed skills.

## Which approach should I use?

- **Point your assistant at the docs** is a good fit for a one-off task or when you can't install packages, and it always reflects the latest published docs.
- **Install the HoloViz skills** gives your assistant packaged, opinionated guidance that works offline, but you need to update it as hvPlot evolves.

## What to do next

- Browse the full list of skills and usage instructions at [holoviz-dev.github.io/holoviz-skills](https://holoviz-dev.github.io/holoviz-skills/).
- If you're contributing to hvPlot, see the [Developer Guide](../developer_guide.md) for how the Markdown docs and `llms.txt` are built.
