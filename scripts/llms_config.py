"""Config for building hvPlot markdown docs and llms.txt."""

from pathlib import Path

from nbsite.scripts import LlmsBuildConfig, LlmsSection, MarkdownSource

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / 'doc'
BUILTDOCS_DIR = ROOT / 'builtdocs'
OUTPUT_DIR = BUILTDOCS_DIR / 'markdown'

# Files that carry no LLM code-gen value and should be excluded from the build.
EXCLUDE_FILES = (
    Path('releases.md'),
    Path('roadmap.md'),
    Path('about.md'),
    Path('developer_guide.md'),
    # Nav-index pages that are pure toctree listings with no inline content.
    Path('tutorials/index.md'),
    Path('ref/index.md'),
    Path('ref/api_compatibility/index.md'),
    Path('gallery/index.rst'),
)

GETTING_STARTED = {
    Path('tutorials/getting_started.md'): 'Installing hvPlot and creating your first plots',
    Path('tutorials/getting_started_pandas.md'): 'Using hvPlot with a Pandas DataFrame',
    Path('ref/installation.md'): 'Installing hvPlot',
}

REFERENCE = {
    Path('ref/api/index.md'): 'Overview of the hvPlot API',
    Path('ref/api_compatibility/pandas/Pandas_API.md'): 'Pandas vs hvPlot API comparison',
    Path('ref/data_libraries.md'): 'Working with data libraries supported by hvPlot',
    Path('ref/plotting_extensions.md'): 'Plotting backends and extensions',
    Path('ref/plotting_options/index.md'): 'Options to control appearance and behavior of plots',
    Path('ref/deprecations.md'): 'Deprecated features and migration notes',
}


def _label(path: Path) -> str:
    """Title-cased label, using parent dir name for index pages."""
    stem = path.parent.name if path.stem == 'index' else path.stem
    return stem.replace('_', ' ').replace('-', ' ').title()


def dict_filter(mapping: dict[Path, str]):
    return lambda path: path in mapping


def dict_description(mapping: dict[Path, str]):
    return lambda path: mapping[path]


CONFIG = LlmsBuildConfig(
    project_title='hvPlot',
    project_description=(
        'hvPlot is a high-level and interactive Pandas-like .plot() API built on '
        'HoloViews,\nletting you visualize data from Pandas, Xarray, GeoPandas, Dask, '
        'Polars, and DuckDB with a familiar interface.\n'
        'This file lists the most important documentation pages for LLM-assisted '
        'development; not all generated doc links are shown.'
    ),
    markdown_root=OUTPUT_DIR,
    llms_output_path=BUILTDOCS_DIR / 'llms.txt',
    markdown_base_url='/markdown',
    sources=(
        MarkdownSource(
            source_dir=DOC_DIR,
            output_dir=OUTPUT_DIR,
            rendered_source_dir=BUILTDOCS_DIR,
            exclude_dir_names=('.ipynb_checkpoints', 'user_guide', 'governance'),
            exclude_files=EXCLUDE_FILES,
        ),
    ),
    sections=(
        LlmsSection(
            title='getting started',
            description='Guides for installing hvPlot and creating your first plots',
            path_prefix=Path('.'),
            path_filter=dict_filter(GETTING_STARTED),
            label_builder=_label,
            description_builder=dict_description(GETTING_STARTED),
            group='Documentation',
        ),
        LlmsSection(
            title='reference',
            description='Overview, compatibility, and configuration pages',
            path_prefix=Path('ref'),
            path_filter=dict_filter(REFERENCE),
            label_builder=_label,
            description_builder=dict_description(REFERENCE),
            group='Documentation',
        ),
        LlmsSection(
            title='gallery',
            description='Example plots organized by category. '
            'Category index pages contain links to all examples in that category.',
            path_prefix=Path('gallery'),
            path_filter=lambda p: p.stem != 'index',
            url_pattern='/markdown/gallery/{path}.md',
            group='Documentation',
        ),
        LlmsSection(
            title='Plotting Options',
            description='Configuration options for controlling how data is styled and displayed.',
            path_prefix=Path('ref/plotting_options'),
            path_filter=lambda p: p.stem != 'index',
            url_pattern='/markdown/ref/plotting_options/{stem}.md',
        ),
        LlmsSection(
            title='API Reference',
            description='Per-method reference pages with signatures, parameters, and examples.',
            path_prefix=Path('ref/api/manual'),
            url_pattern='/markdown/ref/api/manual/{stem}.md',
        ),
    ),
)
