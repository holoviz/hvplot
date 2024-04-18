"""Urls in docstrings etc. should be valid and secure, i.e.

- exist, i.e. provide a 200 response
- use https:// instead of http:// unless
    - https:// is not supported by the web site
    - https:// cannot be used. For example in SVGs.
"""

import pathlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen
import glob

import pytest

# Note: The regex will find urls from code cells in notebooks ending with '\\' because the are really inside \"some_url\"
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"  # pylint: disable=line-too-long
ROOT = pathlib.Path(__file__).parent
PACKAGE_ROOT = ROOT.parent
MAX_WORKERS = 10
POST_FIXES = ['.py', '.ipynb', '.md', '.yaml']
SKIP_URLS = [
    'https://anaconda.org/anaconda/hvplot',
    'https://anaconda.org/conda-forge/hvplot',
    'https://anaconda.org/pyviz/hvplot',
    'https://creativecommons.org/publicdomain/zero/1.0/',
    'https://github.com/rasterio/rasterio',
    'https://www.dask.org',
    'pyproject.toml/equivalent',
]


def _get_files_to_check():
    for post_fix in POST_FIXES:
        for file in glob.glob('**/*' + post_fix, recursive=True):
            yield pathlib.Path(file)


FIXTURES = [pytest.param(file, id=str(file)) for file in _get_files_to_check()]


def _skip_url(url: str):
    if url in SKIP_URLS:
        return True
    if url.startswith('https://github.com/holoviz/hvplot/pull/'):
        return True
    if url.startswith('https://img.shields.io'):
        return True
    if url.startswith('assets.holoviews.org/data/'):
        return True
    if url.startswith('Math.PI'):
        return True
    return False


def _clean_url(url: str):
    if url.endswith('\\'):
        return url[0:-1]
    return url


def _find_urls(text):
    url = re.findall(URL_REGEX, text)
    return {_clean_url(x[0]) for x in url if not _skip_url(x[0])}


def _request_a_response(url):
    return urlopen(url)


def _verify_urls(urls):
    """Returns True if all urls are valid"""
    futures = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for url in urls:
            futures[executor.submit(_request_a_response, url)] = url

        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
            except Exception as ex:
                raise ValueError(f'The url {url} raised an exception') from ex
            if not result.status == 200:
                raise ValueError(f'The url {url} responded with status {result.status}, not 200.')

        return True


# @pytest.mark.parametrize(["file"], FIXTURES)
# def test_urls(file: pathlib.Path):
#     """The urls is docstring should be valid"""
#     # Given
#     text = file.read_text()
#     urls = _find_urls(text)
#     # When/ Then
#     assert _verify_urls(urls)
