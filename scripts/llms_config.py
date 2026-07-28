"""Config for building hvPlot markdown docs and llms.txt
from the nbsite llms builder.
"""

from __future__ import annotations

from pathlib import Path

from nbsite.scripts import LlmsBuildConfig, LlmsSection, MarkdownSource

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / 'doc'
BUILTDOCS_DIR = ROOT / 'builtdocs'
OUTPUT_DIR = BUILTDOCS_DIR / 'markdown'
MARKDOWN_BASE_URL = '/markdown'


def _section_label(path: Path) -> str:
    if path.stem == 'index':
        return 'home' if path.parent == Path('.') else path.parent.as_posix().replace('-', ' ')
    return path.stem.replace('_', ' ')


def _api_label(path: Path) -> str:
    name = path.stem
    for prefix in ('hvplot.hvPlot.', 'hvplot.plotting.'):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            break
    return name.replace('_', ' ')


CONFIG = LlmsBuildConfig(
    project_title='hvPlot',
    project_description=(
        'hvPlot is a high-level plotting API for the HoloViz ecosystem built on HoloViews. \n'
        'This file points to the selected markdown documentation for code-writing utility.'
    ),
    markdown_root=OUTPUT_DIR,
    llms_output_path=BUILTDOCS_DIR / 'llms.txt',
    markdown_base_url=MARKDOWN_BASE_URL,
    sources=(MarkdownSource(source_dir=DOC_DIR, output_dir=OUTPUT_DIR),),
    sections=(
        LlmsSection(
            title='Home',
            description='Top-level pages in the hvPlot docs tree.',
            path_prefix=Path('.'),
            label_builder=_section_label,
            path_filter=lambda path: len(path.parts) == 1,
        ),
        LlmsSection(
            title='Tutorials',
            description='Step-by-step guides to help you master hvPlot and the HoloViz ecosystem.',
            path_prefix=Path('tutorials'),
        ),
        LlmsSection(
            title='Gallery',
            description='Example visualizations using hvPlot with different backends and datasets',
            path_prefix=Path('gallery'),
        ),
        LlmsSection(
            title='Reference',
            description="API reference pages that provide detailed info about hvPlot's usage.",
            path_prefix=Path('ref'),
            label_builder=_section_label,
            path_filter=lambda path: not path.is_relative_to(Path('ref/api/manual')),
        ),
        LlmsSection(
            title='API',
            description='hvPlot plotting APIs.',
            path_prefix=Path('ref/api/manual'),
            label_builder=_api_label,
        ),
    ),
)
