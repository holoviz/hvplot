import json
import os
import sys
import shutil

from setuptools import setup, find_packages

import pyct.build

def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path))['version_string']


########## dependencies ##########

install_requires = [
    'bokeh >=1.0.0',
    'colorcet >=2',
    'holoviews >=1.11.0',
    'pandas',
    'numpy>=1.15',
    'packaging',
    'panel >=0.11.0',
]

_examples = [
    'geoviews >=1.6.0',
    'numba >=0.51.0',
    'geopandas',
    'xarray >=0.18.2',
    'networkx >=2.6.3',
    'streamz >=0.3.0',
    'intake >=0.6.5',
    'intake-parquet >=0.2.3',
    'intake-xarray >=0.5.0',
    'dask >=2021.3.0',
    'datashader >=0.6.5',
    'notebook >=5.4',
    'rasterio',
    'cartopy',
    'pyproj',
    's3fs >=2022.1.0',
    'scipy >=1.5.3',
    'pillow >=8.2.0',
    'selenium >=3.141.0',
    'spatialpandas >=0.4.3',
    'scikit-image >=0.17.2',
    'python-snappy >=0.6.0',
    'pooch >=1.6.0',
    'fiona',
    'rioxarray',
    # Extra dependency of cartopy on Python 3.6 only
    'pyepsg',
    'matplotlib',
    'plotly',
    'pygraphviz',
    'ipykernel <6.18.0'  # temporary
]

extras_require = {
    'tests': [
        'codecov',
        'flake8',
        'parameterized',
        'pytest',
        'pytest-cov',
        'nbsmoke >=0.2.0',
        'numpy >=1.7',
        'matplotlib',
        'plotly',
        'xarray',
        'pooch',
        'scipy',
        'ipywidgets',
        'pre-commit',
    ],
    'examples': _examples,
    'doc': _examples + [
        'nbsite >=0.7.2rc2',
        'pydata-sphinx-theme <0.10',
        'sphinx-copybutton',
        'sphinx-design',
    ]
}

# until pyproject.toml/equivalent is widely supported (setup_requires
# doesn't work well with pip)
extras_require['build'] = [
    'param >=1.6.1',
    'pyct >=0.4.4',
    'setuptools' # should make this pip now
]

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

########## metadata for setuptools ##########

setup_args = dict(
    name='hvplot',
    version=get_setup_version("hvplot"),
    description='A high-level plotting API for the PyData ecosystem built on HoloViews.',
    long_description=open("README.md", mode="r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author= "Philipp Rudiger",
    author_email= "developers@pyviz.org",
    maintainer="HoloViz developers",
    maintainer_email="developers@pyviz.org",
    packages=find_packages(),
    include_package_data=True,
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='https://hvplot.pyviz.org',
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests'],
    entry_points={
        'console_scripts': [],
        'pandas_plotting_backends': [
            'holoviews = hvplot:plotting',
        ],
    },
)


if __name__ == '__main__':
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'hvplot','examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
