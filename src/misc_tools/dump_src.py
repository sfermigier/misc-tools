#!/usr/bin/env python
"""
Usage:
    python script_name.py <source_path> [--suffix <suffix_string>]
Example:
    python script_name.py ./my_folder --suffix .py
    python script_name.py /var/log
"""

import argparse
import sys
from pathlib import Path


def main():
    """Parses arguments and prints them."""

    parser = argparse.ArgumentParser(
        description='Dump a source tree to stdout.',
    )

    parser.add_argument(
        '--suffix',
        dest='suffix',
        metavar='SUFFIX_STRING',
        type=str,
        help='Optional file suffix to filter by (e.g., "py").'
    )

    parser.add_argument(
        'srcs',
        metavar='SOURCE_PATH',
        type=str,
        default=[],
        nargs='+',
        help='The source path to process.'
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            print("Error: Invalid arguments provided.")
            parser.print_help()
        sys.exit(e.code)

    suffix = args.suffix

    for src in args.srcs:
        src_path = Path(src)

        if suffix:
            files = sorted(src_path.rglob(f"*.{suffix}"))
        else:
            files = sorted(src_path.rglob("*"))

        for path in files:
            dump_file(path)


def dump_file(path):
    if not path.is_file():
        return

    if path.name.startswith("."):
        return

    if any(part.startswith(".") for part in path.parts):
        return

    actual_suffix = path.suffix[1:]
    match actual_suffix:
        case "py" | "php":
            print(78 * "#")
            print(f"# File: {path}")
            print(78 * "#")
        case "js" | "ts":
            print("// " + 70 * "-")
            print(f"// File: {path}")
            print("// " + 70 * "-")
        case "md" | "html" | "xml":
            print("<!-- " + 70 * "-" + "-->")
            print(f"<!-- File: {path} -->")
            print("<!-- " + 70 * "-" + "-->")
        case "java" | "groovy" | "c" | "cpp" | "h" | "css" | "oss":
            print("/* " + 70 * "-" + " */")
            print(f"/* File: {path} */")
            print("/* " + 70 * "-" + " */")
        case "pyc":
            return
        case _:
            print("Unknown file type", file=sys.stderr)
            print(f"File: {path}")
            print("" + 70 * "-")

    print()
    text = path.read_text()
    print(text)
    print()
    print()

    print(f"{len(text)} bytes - {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
