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


def _test_paths() -> set[Path]:
    return llms_config.PAGES | llms_config.ROOT_PAGES


def _resolve_doc_path(path: Path) -> Path | None:
    """Return the source file in ``doc/`` a configured page maps to, if any."""
    stem = path.with_suffix('')
    for suffix in SOURCE_SUFFIXES:
        candidate = llms_config.DOC_DIR / f'{stem}{suffix}'
        if candidate.exists():
            return candidate
    return None


def _matches(section, path: Path) -> bool:
    prefix = section.path_prefix
    matches_prefix = prefix in {Path(), Path('.')} or path.is_relative_to(prefix)
    return matches_prefix and section.path_filter(path)


def test_config_is_valid() -> None:
    assert isinstance(llms_config.CONFIG, LlmsBuildConfig)


@pytest.mark.parametrize('path', sorted(_test_paths()))
def test_referenced_pages_exist(path: Path) -> None:
    assert _resolve_doc_path(path) is not None


def test_sections_match_at_least_one_page() -> None:
    for section in llms_config.CONFIG.sections:
        assert any(_matches(section, path) for path in _test_paths())


@pytest.mark.parametrize('section', llms_config.CONFIG.sections, ids=lambda s: s.title)
def test_section_labels_are_unique_and_non_empty(section) -> None:
    paths = [path for path in _test_paths() if _matches(section, path)]
    labels = [section.label_builder(path) for path in paths]
    assert all(labels)
    assert len(labels) == len(set(labels))
