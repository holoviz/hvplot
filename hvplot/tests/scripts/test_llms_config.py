"""Tests for the nbsite LLM documentation build config (scripts/llms_config.py).

The ``llms_config`` module requires ``nbsite``, which is only a doc
dependency, so the tests are skipped when it is not installed.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip('nbsite')

REPO_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(REPO_ROOT / 'scripts'))

import llms_config  # noqa: E402
from nbsite.scripts import LlmsBuildConfig  # noqa: E402

SOURCE_SUFFIXES = ('.md', '.ipynb', '.rst')


def _all_doc_paths() -> set[Path]:
    """Every markdown path the sources produce, relative to the markdown root."""
    paths: set[Path] = set()
    for source in llms_config.CONFIG.sources:
        for path in source.source_dir.rglob('*'):
            if not path.is_file():
                continue
            rel_path = path.relative_to(source.source_dir)
            if any(part in source.exclude_dir_names for part in rel_path.parts):
                continue
            if rel_path.suffix not in source.include_suffixes:
                continue
            paths.add(rel_path.with_suffix('.md'))
    return paths


def _matches(section, path: Path) -> bool:
    prefix = section.path_prefix
    matches_prefix = prefix in {Path(), Path('.')} or path.is_relative_to(prefix)
    return matches_prefix and section.path_filter(path)


def _section_paths(section) -> list[Path]:
    return [path for path in sorted(_all_doc_paths()) if _matches(section, path)]


def test_config_is_valid() -> None:
    assert isinstance(llms_config.CONFIG, LlmsBuildConfig)


def test_every_section_matches_at_least_one_page() -> None:
    for section in llms_config.CONFIG.sections:
        assert _section_paths(section)


@pytest.mark.parametrize('section', llms_config.CONFIG.sections, ids=lambda s: s.title)
def test_section_labels_are_unique_and_non_empty(section) -> None:
    paths = _section_paths(section)
    labels = [section.label_builder(path) for path in paths]
    assert all(labels)
    assert len(labels) == len(set(labels))


@pytest.mark.parametrize('section', llms_config.CONFIG.sections, ids=lambda s: s.title)
def test_section_descriptions_are_non_empty(section) -> None:
    assert section.description.strip()
    if section.description_builder is not None:
        for path in _section_paths(section):
            assert section.description_builder(path).strip()
