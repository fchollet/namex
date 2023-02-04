import os
import sys
import importlib

INIT_FILE_HEADER = """DO NOT EDIT.

This file was autogenerated. Do not edit it by hand,
since your modifications would be overwritten.


"""


def generate_api_files(package, code_directory="src", verbose=False):
    """Writes out API export `__init__.py` files.

    Given a codebase structured as such:

    ```
    package/
    ...src/
    ......__init__.py
    ......(Python files that use e.g. `@export_api(package="package", export_path="package.x.y.Z")`)
    ```

    this script generates `__init__.py` files within `package/`
    to export the public API described by the `@api_export` calls.

    Important notes:

    * Any existing `__init__.py` files in `package/` but outside of
        `package/code_directory/` may be overwritten.
    * This script must be run in an environment that includes
        all dependencies used by `package`. Make sure to install
        them before running the script.
    """
    if verbose:
        print(
            f"Generating files for package '{package}' "
            f"from sources found in '{package}/{code_directory}'."
        )

    if not os.path.exists(package):
        raise ValueError(f"No directory named '{package}'.")
    if not os.path.exists(os.path.join(package, code_directory)):
        raise ValueError(f"No directory named '{package}/{code_directory}'.")

    # Make list of all Python files (modules) to visit.
    codebase_walk_entry_points = []
    for root, _, files in os.walk(os.path.join(package, code_directory)):
        for fname in files:
            if fname == "__init__.py":
                codebase_walk_entry_points.append(".".join(root.split("/")))
            elif fname.endswith(".py") and not fname.endswith("_test.py"):
                module_name = fname[:-3]
                codebase_walk_entry_points.append(
                    ".".join(root.split("/")) + "." + module_name
                )

    # Import all Python modules found in the code directory.
    sys.path.insert(0, os.getcwd())
    modules = []
    for entry_point in codebase_walk_entry_points:
        mod = importlib.import_module(entry_point, package=".")
        modules.append(mod)

    if verbose:
        print("Compiling list of symbols to export.")

    # Populate list of all symbols to register.
    all_symbols = set()
    for module in modules:
        for name in dir(module):
            if name.startswith("_"):
                continue
            symbol = getattr(module, name)
            if not hasattr(symbol, "_api_export_path"):
                continue
            if not all(
                [
                    path.startswith(package + ".")
                    for path in to_list(symbol._api_export_path)
                ]
            ):
                continue
            all_symbols.add(symbol)

    # Generate __init__ files content.
    init_files_content = {}
    for symbol in all_symbols:
        if verbose:
            print(f"...processing symbol '{symbol.__name__}'")
        for export_path in to_list(symbol._api_export_path):
            export_modules = export_path.split(".")
            export_name = export_modules[-1]
            parent_path = os.path.join(*export_modules[:-1])
            if parent_path not in init_files_content:
                init_files_content[parent_path] = []
            init_files_content[parent_path].append(
                {"symbol": symbol, "export_name": export_name}
            )
            for i in range(1, len(export_modules[:-1])):
                intermediate_path = os.path.join(*export_modules[:i])
                if intermediate_path not in init_files_content:
                    init_files_content[intermediate_path] = []
                init_files_content[intermediate_path].append(
                    {
                        "module": export_modules[i],
                        "location": ".".join(export_modules[:i]),
                    }
                )

    if verbose:
        print("Writing out API files.")

    # Go over init_files_content, make dirs,
    # create __init__.py file, populate file with public symbol imports.
    for path, contents in init_files_content.items():
        os.makedirs(path, exist_ok=True)
        init_file_lines = []
        for symbol_metadata in contents:
            if "symbol" in symbol_metadata:
                symbol = symbol_metadata["symbol"]
                name = symbol_metadata["export_name"]
                init_file_lines.append(
                    f"from {symbol.__module__} import {symbol.__name__} as {name}"
                )
            elif "module" in symbol_metadata:
                init_file_lines.append(
                    f"from {'.'.join(path.split('/'))} import {symbol_metadata['module']}"
                )

        init_path = os.path.join(path, "__init__.py")
        if verbose:
            print(f"...writing {init_path}")
        with open(init_path, "w") as f:
            contents = INIT_FILE_HEADER + "\n".join(init_file_lines) + "\n"
            f.write(contents)


def to_list(x):
    if isinstance(x, (list, tuple)):
        return list(x)
    elif isinstance(x, str):
        return [x]
    return []
