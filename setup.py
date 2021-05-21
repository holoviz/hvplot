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
        return json.load(open(version_file_path, 'r'))['version_string']


########## dependencies ##########

install_requires = [
    'bokeh >=1.0.0',
    'colorcet >=2',
    'holoviews >=1.11.0',
    'pandas',
    'numpy>=1.15'
]

_examples = [
    'geoviews >=1.6.0',
    'numba >=0.51.0',
    'geopandas',
    'xarray <0.17.0',
    'networkx',
    'streamz >=0.3.0',
    'intake',
    'intake-parquet',
    'intake-xarray',
    'dask',
    'datashader >=0.6.5',
    'notebook >=5.4',
    'rasterio',
    's3fs',
    'scipy',
    'pillow',
    'selenium',
    'spatialpandas',
    'scikit-image',
    'python-snappy',
    'pyepsg'
]

_examples_extra = _examples + [
    'pygraphviz',
]

extras_require = {
    'tests': [
        'coveralls',
        'nose',
        'flake8',
        'parameterized',
        'pytest',
        'nbsmoke >=0.2.0',
        'twine',   # required for pip packaging
        'rfc3986', # required by twine
        'keyring', # required by twine
        'numpy >=1.7,<1.20' # Numba ABI incompatibility
    ],
    'examples': _examples,
    'examples_extra': _examples_extra,
    'doc': _examples_extra + [
        'nbsite >=0.5.1',
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
    long_description=open("README.md").read(),
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"],
    python_requires=">=2.7",
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
