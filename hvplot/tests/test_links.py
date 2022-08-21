"""Urls in docstrings etc. should be valid"""

import pathlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

import pytest

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
ROOT = pathlib.Path(__file__).parent
PACKAGE_ROOT = ROOT.parent
MAX_WORKERS = 10


def _get_files_to_check():
    return [PACKAGE_ROOT / "plotting" / "core.py"]


FIXTURES = [pytest.param(file, id=file.name) for file in _get_files_to_check()]


def _find_urls(text):
    url = re.findall(URL_REGEX, text)
    return set(x[0] for x in url)


def _url_exists(url):
    return urlopen(url).status == 200


def _verify_urls(urls):
    """Returns True if all urls are valid"""
    futures = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for url in urls:
            futures[executor.submit(_url_exists, url)] = url

        for future in as_completed(futures):
            url = futures[future]
            try:
                if not _url_exists(url):
                    raise ValueError(f"The url {url} did not respond with status 200.")
            except Exception as ex:  # pylint: disable=broad-except
                raise ValueError(f"The url {url} did not respond with status 200.") from ex
    return True


@pytest.mark.parametrize(["file"], FIXTURES)
def test_urls(file: pathlib.Path):
    """The urls is docstring should be valid"""
    # Given
    text = file.read_text()
    urls = _find_urls(text)
    # When/ Then
    assert _verify_urls(urls)
