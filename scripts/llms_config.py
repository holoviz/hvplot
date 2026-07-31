"""Config for building hvPlot markdown docs and llms.txt."""

from __future__ import annotations

from pathlib import Path

from nbsite.scripts import LlmsBuildConfig, LlmsSection, MarkdownSource

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / 'doc'
BUILTDOCS_DIR = ROOT / 'builtdocs'
OUTPUT_DIR = BUILTDOCS_DIR / 'markdown'
MARKDOWN_BASE_URL = '/markdown'

PAGES = {
    Path('index.md'),
    Path('about.md'),
    Path('developer_guide.md'),
    Path('releases.md'),
    Path('roadmap.md'),
    Path('ref/index.md'),
    Path('ref/deprecations.md'),
    Path('ref/installation.md'),
    Path('ref/api/index.md'),
    Path('ref/api_compatibility/pandas/index.md'),
    Path('ref/plotting_options/index.md'),
    Path('ref/plotting_options/axis.md'),
    Path('ref/plotting_options/data.md'),
    Path('ref/plotting_options/geographic.md'),
    Path('ref/plotting_options/interactivity.md'),
    Path('ref/plotting_options/legend.md'),
    Path('ref/plotting_options/size_layout.md'),
    Path('ref/plotting_options/styling.md'),
    Path('ref/api/manual/hvplot.hvPlot.area.md'),
    Path('ref/api/manual/hvplot.hvPlot.bar.md'),
    Path('ref/api/manual/hvplot.hvPlot.explorer.md'),
    Path('ref/api/manual/hvplot.hvPlot.heatmap.md'),
    Path('ref/api/manual/hvplot.hvPlot.line.md'),
    Path('ref/api/manual/hvplot.hvPlot.points.md'),
    Path('ref/api/manual/hvplot.hvPlot.scatter.md'),
}

ROOT_PAGES = {
    Path('index.md'),
    Path('about.md'),
    Path('developer_guide.md'),
    Path('releases.md'),
    Path('roadmap.md'),
}


def _index_label(path: Path) -> str:
    return 'home' if path.parent == Path('.') else path.parent.as_posix().replace('-', ' ')


def _label(path: Path) -> str:
    if path.stem == 'index':
        return _index_label(path)
    return path.stem.replace('_', ' ')


def _api_label(path: Path) -> str:
    if path.stem == 'index':
        return _index_label(path)
    name = path.stem
    for prefix in ('hvplot.hvPlot.', 'hvplot.plotting.', 'hvplot.ui.', 'hvplot.networkx.'):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            break
    return name.replace('_', ' ')


CONFIG = LlmsBuildConfig(
    project_title='hvPlot',
    project_description='hvPlot documentation selected for LLM-friendly browsing.',
    markdown_root=OUTPUT_DIR,
    llms_output_path=BUILTDOCS_DIR / 'llms.txt',
    markdown_base_url=MARKDOWN_BASE_URL,
    sources=(
        MarkdownSource(
            source_dir=DOC_DIR,
            output_dir=OUTPUT_DIR,
            exclude_dir_names=('.ipynb_checkpoints', 'user_guide'),
        ),
    ),
    sections=(
        LlmsSection(
            title='Home',
            description='Top-level pages and project overview.',
            path_prefix=Path('.'),
            path_filter=lambda path: path in ROOT_PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title='Reference',
            description='Installation notes and reference overview pages.',
            path_prefix=Path('ref'),
            path_filter=lambda path: path in PAGES,
            label_builder=_api_label,
        ),
        LlmsSection(
            title='Plotting Options',
            description='Core plotting configuration topics.',
            path_prefix=Path('ref/plotting_options'),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
        LlmsSection(
            title='API Manual',
            description='Representative hvPlot API examples.',
            path_prefix=Path('ref/api/manual'),
            path_filter=lambda path: path in PAGES,
            label_builder=_api_label,
        ),
        LlmsSection(
            title='API Compatibility',
            description='Compatibility notes for external plotting backends.',
            path_prefix=Path('ref/api_compatibility'),
            path_filter=lambda path: path in PAGES,
            label_builder=_label,
        ),
    ),
)
