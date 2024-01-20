import argparse
import os
import difflib

import hvplot
import panel as pn

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


def ensure_variable_exists(data, input_, variables):
    if input_ is None:
        return

    if input_ not in variables:
        fuzzy_matches = difflib.get_close_matches(input_, variables, n=1)
        if fuzzy_matches:
            print(f"Using {fuzzy_matches[0]} instead of {input_!r}")
            input_ = fuzzy_matches[0]
        else:
            raise ValueError(
                f"{input_!r} not in data, available variables are {variables!r}"
            )
    return input_


def parse_inputs(inputs):
    kwargs = {}
    if not inputs:
        return kwargs

    for input_ in inputs:
        key, value = input_.split("=")
        if "," in value:
            value = [v for v in value.strip("[]").strip("()").split(",") if v]
        elif value.lower() in ("true", "false"):
            value = value == "true"
        kwargs[key] = value
    return kwargs


def parse_arguments():
    parser = argparse.ArgumentParser(description="hvPlot CLI")
    parser.add_argument("file_path", type=str, help="Path to the data file")
    parser.add_argument(
        "hvplot_kwargs", nargs="*", help="HoloViews options in 'key=value' format"
    )
    parser.add_argument(
        "--opts", nargs="*", help="HoloViews plot options in 'key=value' format"
    )
    parser.add_argument(
        "--reader_kwargs",
        type=str,
        help="Reader options in 'key=value' format",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5006,
    )
    parser.add_argument("--output_path", type=str, help="Path to save the output file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Process file extension
    path, extension = os.path.splitext(args.file_path)
    setup_extension_readers(extension)

    # Determine and use the appropriate file reader
    reader_kwargs = {}
    try:
        reader, reader_kwargs = _EXTENSION_READERS[extension]
    except KeyError:
        raise NotImplementedError(f"Extension {extension} not supported")
    reader_kwargs.update(parse_inputs(args.reader_kwargs))
    data = reader(args.file_path, **reader_kwargs)

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
