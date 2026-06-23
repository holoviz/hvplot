"""
Build markdown docs and llms.txt for hvPlot's LLM-facing documentation set.

Run as part of the docs build pipeline:
    pixi run docs-build
"""

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOC_DIR = ROOT / 'doc'
BUILTDOCS_DIR = ROOT / 'builtdocs'
OUTPUT_DIR = BUILTDOCS_DIR / 'markdown'
MARKDOWN_BASE_URL = '/markdown'

INCLUDED_REFERENCE_FILES = {
    Path('ref/index.md'),
    Path('ref/installation.md'),
    Path('ref/data_libraries.ipynb'),
    Path('ref/plotting_extensions.ipynb'),
    Path('ref/deprecations.md'),
    Path('ref/api/index.md'),
}

INCLUDED_DIR_PREFIXES = (
    Path('tutorials'),
    Path('ref/plotting_options'),
    Path('ref/api/manual'),
    Path('ref/api_compatibility'),
)

EXCLUDED_DIR_NAMES = {'gallery', 'user_guide', '.ipynb_checkpoints'}


def _is_included(rel_path: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in rel_path.parts):
        return False

    if rel_path.suffix not in {'.md', '.ipynb'}:
        return False

    if rel_path in INCLUDED_REFERENCE_FILES:
        return True

    return any(rel_path.is_relative_to(prefix) for prefix in INCLUDED_DIR_PREFIXES)


def _iter_source_docs() -> list[Path]:
    docs = [
        path
        for path in DOC_DIR.rglob('*')
        if path.is_file() and _is_included(path.relative_to(DOC_DIR))
    ]
    return sorted(docs)


def _convert_notebook(notebook_path: Path, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'jupyter',
            'nbconvert',
            '--to',
            'markdown',
            '--output-dir',
            str(output_dir),
            str(notebook_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        rel = notebook_path.relative_to(DOC_DIR)
        print(f'  Warning: failed to convert {rel}: {result.stderr.strip()}')
        return False
    return True


def build_markdown_docs() -> list[Path]:
    generated: list[Path] = []
    for source in _iter_source_docs():
        rel = source.relative_to(DOC_DIR)
        destination_dir = OUTPUT_DIR / rel.parent

        if source.suffix == '.md':
            destination = OUTPUT_DIR / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            generated.append(rel)
            print(f'  Copied {rel}')
            continue

        if _convert_notebook(source, destination_dir):
            generated.append(rel.with_suffix('.md'))
            print(f'  Converted {rel}')

    return generated


def _default_label(path: Path) -> str:
    return path.stem.replace('_', ' ')


def _api_manual_label(path: Path) -> str:
    name = path.stem
    for prefix in ('hvplot.hvPlot.', 'hvplot.plotting.'):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            break
    return name.replace('_', ' ')


def _reference_label(path: Path) -> str:
    if path.stem != 'index':
        return _default_label(path)

    if path.parent == Path('ref'):
        return 'reference'

    return path.parent.name.replace('_', ' ')


def _build_links(
    paths: list[Path], label_builder: Callable[[Path], str] = _default_label
) -> list[str]:
    return [
        f'- [{label_builder(path)}]({MARKDOWN_BASE_URL}/{path.as_posix()})'
        for path in sorted(paths)
    ]


def generate_llms_txt(generated_paths: list[Path]) -> None:
    tutorial_paths = [p for p in generated_paths if p.is_relative_to(Path('tutorials'))]
    ref_paths = [
        p
        for p in generated_paths
        if p.is_relative_to(Path('ref')) and not p.is_relative_to(Path('ref/api/manual'))
    ]
    api_manual_paths = [p for p in generated_paths if p.is_relative_to(Path('ref/api/manual'))]

    lines = [
        '# hvPlot',
        '',
        'hvPlot is a high-level plotting API for the HoloViz ecosystem built on HoloViews.',
        'This file points to markdown documentation selected for code-writing utility.',
        '',
        f'All links resolve under {MARKDOWN_BASE_URL}/.',
        '',
    ]

    if tutorial_paths:
        lines.extend(['## Tutorials', ''])
        lines.extend(
            [
                'Step-by-step guides to help you master hvPlot and explore the full HoloViz ecosystem.',
                '',
            ]
        )
        lines.extend(_build_links(tutorial_paths))
        lines.append('')

    if ref_paths:
        lines.extend(['## Reference', ''])
        lines.extend(
            ['API reference and pages that provide detailed information about hvPlot’s usage.', '']
        )
        lines.extend(_build_links(ref_paths, _reference_label))
        lines.append('')

    if api_manual_paths:
        lines.extend(['## API', ''])
        lines.extend(['hvPlot plotting APIs', ''])
        lines.extend(_build_links(api_manual_paths, _api_manual_label))
        lines.append('')

    llms_txt = BUILTDOCS_DIR / 'llms.txt'
    llms_txt.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Generated {llms_txt}')


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print('Building markdown docs for hvPlot scope...')
    generated = build_markdown_docs()
    print('Generating llms.txt...')
    generate_llms_txt(generated)
    print('Done!')


if __name__ == '__main__':
    main()
