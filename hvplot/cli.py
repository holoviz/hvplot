import argparse
import os

import panel as pn

HELP_DESCRIPTION = """
This command-line tool allows for quick and easy visualization of various
data file formats using HoloViews and hvPlot, including CSV, JSON, HTML, Excel,
Parquet, NetCDF, and HDF5, and more.

The tool will automatically determine the appropriate reader for the file
extension and use it to load the data. Ensure the correct dependencies for
file format support are installed (e.g., pandas for CSV, xarray for NetCDF).

All of the keywords supported by hvPlot can be passed as arguments to the
command-line tool. See the hvPlot customization docs for available kwargs:
https://hvplot.holoviz.org/user_guide/Customization.html

Examples:
    hvplot iris.csv
    hvplot air.nc x=lon y=lat groupby=time,level geo=true
    hvplot detrend.nino34.ascii.txt x=YR y=ANOM -r pandas.read_csv -rk delimiter='\s+'
"""

_MODULES_KWARGS = {
    "xarray": {
        "extensions": [".nc", ".hdf5", ".h5", ".zarr", ".grib"],
        "default_reader": "open_dataset",
        "extras": {
            ".zarr": {"kwargs": {"engine": "zarr"}},
            ".grib": {"kwargs": {"engine": "cfgrib"}},
        },
    },
    "pandas": {
        "extensions": [".csv", ".json", ".html", ".xls", ".xlsx", ".parquet"],
        "default_reader": "read_csv",
        "extras": {
            ".json": {"reader": "read_json"},
            ".html": {"reader": "read_html"},
            ".xls": {"reader": "read_excel"},
            ".xlsx": {"reader": "read_excel"},
            ".parquet": {"reader": "read_parquet"},
        },
    },
    "geopandas": {
        "extensions": [".shp", ".geojson", ".gml"],
        "default_reader": "read_file",
    },
}
_EXTENSION_READERS = {}


def import_and_register_module(module_name, extensions, default_reader, extras=None):
    try:
        module = __import__(module_name)
        if module_name == "geopandas":
            module_name = "pandas"  # Ensure hvplot.pandas is imported for geopandas
        __import__("hvplot." + module_name)

        for ext in extensions:
            reader_kwargs = {"reader": default_reader}
            if extras and ext in extras:
                reader_kwargs.update(extras[ext])

            if hasattr(module, reader_kwargs["reader"]):
                _EXTENSION_READERS[ext] = (
                    getattr(module, reader_kwargs["reader"]),
                    reader_kwargs.get("kwargs", {}),
                )
    except ImportError:
        pass


def setup_extension_readers(extension):
    for module_name, module_kwargs in _MODULES_KWARGS.items():
        if extension in module_kwargs["extensions"]:
            import_and_register_module(module_name, **module_kwargs)
            break


def parse_inputs(inputs):
    kwargs = {}
    if not inputs:
        return kwargs

    if isinstance(inputs, str):
        inputs = [inputs]

    for input_ in inputs:
        key, value = input_.split("=")
        if "," in value:
            value = [v for v in value.strip("[]").strip("()").split(",") if v]
        elif value.lower() in ("true", "false"):
            value = value == "true"
        kwargs[key] = value
    return kwargs


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file_path", type=str, help="Path to the data file")
    parser.add_argument(
        "hvplot_kwargs", nargs="*", help="hvPlot arguments in 'key=value' format"
    )
    parser.add_argument(
        "-var", "--variable", type=str, help="Variable to plot (for xarray DataArrays)"
    )
    parser.add_argument(
        "--opts", nargs="*", help="HoloViews plot options in 'key=value' format"
    )
    parser.add_argument(
        "-r",
        "--reader",
        type=str,
        help="Fully-qualified name of the data-reader function to use, e.g. pandas.read_csv",
    )
    parser.add_argument(
        "-rk",
        "--reader_kwargs",
        type=str,
        help="Reader options in 'key=value' format",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5006,
        help="Port to use for displaying the plot",
    )
    parser.add_argument(
        "-o", "--output_path", type=str, help="Path to save the output file"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Process file extension
    path, extension = os.path.splitext(args.file_path)
    setup_extension_readers(extension)

    # Determine and use the appropriate file reader
    if args.reader:
        module_name, reader_name = args.reader.rsplit(".", 1)
        import_and_register_module(
            module_name, extensions=[extension], default_reader=reader_name
        )
    try:
        reader, reader_kwargs = _EXTENSION_READERS[extension]
    except KeyError:
        raise NotImplementedError(f"Extension {extension} not supported")
    reader_kwargs.update(parse_inputs(args.reader_kwargs))
    data = reader(args.file_path, **reader_kwargs)
    
    if args.variable:
        data = data[args.variable]

    # Process hvplot kwargs
    hvplot_kwargs = parse_inputs(args.hvplot_kwargs)
    hvplot_kwargs["title"] = hvplot_kwargs.get("title", path)
    hvplot_kwargs["kind"] = hvplot_kwargs.get("kind", "explorer")
    for key in ["groupby", "by", "features"]:
        value = hvplot_kwargs.get(key, None)
        if value and not isinstance(value, list):
            hvplot_kwargs[key] = [value]

    # Process opts
    opts_kwargs = parse_inputs(args.opts)
    if opts_kwargs and hvplot_kwargs["kind"] == "explorer":
        hvplot_kwargs["opts"] = opts_kwargs

    plot = data.hvplot(**hvplot_kwargs)
    if opts_kwargs and hvplot_kwargs["kind"] != "explorer":
        plot = plot.opts(**opts_kwargs)

    if args.output_path:
        plot.save(args.output_path)
    else:
        pn.panel(plot).show(port=args.port)


if __name__ == "__main__":
    main()
