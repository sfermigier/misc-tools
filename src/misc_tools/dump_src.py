#!/usr/bin/env python
"""
Usage:
    dump-src [SOURCE_PATH...] [--suffix SUFFIX_STRING] [-o OUTPUT_FILE] [-x PATH]
Example:
    dump-src ./my_folder --suffix py,php,java
    dump-src /var/log --suffix log
    dump-src src tests --suffix py -o output.md
    dump-src --suffix py -x tests -x __pycache__
    dump-src --suffix py -x file1.py -x file2.py -x build
    dump-src  # Defaults to current directory
"""

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("misc-tools")
except PackageNotFoundError:
    # When running as a script before installation
    __version__ = "unknown"


def is_excluded(path: Path, exclude_paths: list[Path]) -> bool:
    """Check if a path should be excluded."""
    resolved_path = path.resolve()

    for exclude in exclude_paths:
        # Check if path matches the exclude exactly
        if resolved_path == exclude:
            return True

        # Check if path is inside an excluded directory
        try:
            resolved_path.relative_to(exclude)
            return True
        except ValueError:
            # Not a subpath
            continue

    return False


def main():
    """Parses arguments and prints them."""

    parser = argparse.ArgumentParser(
        description="Dump a source tree to stdout or file.",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--suffix",
        dest="suffix",
        metavar="SUFFIX_STRING",
        type=str,
        help='Optional file suffix(es) to filter by (e.g., "py" or "py,php,java").',
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        metavar="OUTPUT_FILE",
        type=str,
        help="Output file (defaults to stdout).",
    )

    parser.add_argument(
        "-x",
        "--exclude",
        dest="excludes",
        metavar="PATH",
        action="append",
        type=str,
        help="Exclude file or directory (can be used multiple times).",
    )

    parser.add_argument(
        "srcs",
        metavar="SOURCE_PATH",
        type=str,
        default=["."],
        nargs="*",
        help="The source path(s) to process (defaults to current directory).",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            print("Error: Invalid arguments provided.", file=sys.stderr)
            parser.print_help()
        sys.exit(e.code)

    # Default to current directory if no sources provided
    if not args.srcs:
        args.srcs = ["."]

    # Parse suffixes (comma-separated)
    suffixes = []
    if args.suffix:
        suffixes = [s.strip() for s in args.suffix.split(",")]

    # Process excludes - convert to resolved Path objects
    exclude_paths = []
    if args.excludes:
        for exclude in args.excludes:
            exclude_path = Path(exclude).resolve()
            exclude_paths.append(exclude_path)

    # Get absolute path of output file to exclude it
    output_path = None
    if args.output:
        output_path = Path(args.output).resolve()

    # Redirect stdout to file if output is specified
    output_file = None
    original_stdout = sys.stdout
    if args.output:
        try:
            output_file = Path(args.output).open("w")
            sys.stdout = output_file
        except OSError as e:
            print(f"Error: Cannot open output file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        for src in args.srcs:
            src_path = Path(src)

            # Check if source is a file or directory
            if src_path.is_file():
                # If it's a file, add it directly
                files = [src_path]
            elif src_path.is_dir():
                # If it's a directory, use rglob
                if suffixes:
                    # Collect files with any of the specified suffixes
                    files = []
                    for suffix in suffixes:
                        files.extend(src_path.rglob(f"*.{suffix}"))
                    files = sorted(set(files))  # Remove duplicates and sort
                else:
                    files = sorted(src_path.rglob("*"))
            else:
                print(f"Error: {src_path} does not exist.", file=sys.stderr)
                continue

            for path in files:
                # Skip the output file if it's in the source tree
                if output_path and path.resolve() == output_path:
                    continue

                # Skip excluded paths
                if is_excluded(path, exclude_paths):
                    continue

                try:
                    dump_file(path)
                except Exception as e:
                    print(f"Error processing file {path}: {e}", file=sys.stderr)
    finally:
        # Restore stdout and close output file
        if output_file:
            sys.stdout = original_stdout
            output_file.close()


def dump_file(path):
    if not path.is_file():
        return

    if path.name.startswith("."):
        return

    if any(part.startswith(".") for part in path.parts):
        return

    actual_suffix = path.suffix[1:].lower()
    match actual_suffix:
        case "py" | "php":
            print(78 * "#")
            print(f"# File: {path}")
            print(78 * "#")
        case "js" | "ts":
            print("// " + 70 * "-")
            print(f"// File: {path}")
            print("// " + 70 * "-")
        case "md" | "html" | "xml" | "txt" | "json" | "yaml" | "yml" | "conf":
            print("<!-- " + 70 * "-" + "-->")
            print(f"<!-- File: {path} -->")
            print("<!-- " + 70 * "-" + "-->")
        case "java" | "groovy" | "c" | "cpp" | "h" | "css" | "oss":
            print("/* " + 70 * "-" + " */")
            print(f"/* File: {path} */")
            print("/* " + 70 * "-" + " */")
        case "pyc" | "db":
            return
        case "lock" | "png" | "jpg" | "jpeg" | "gif" | "svg" | "ico" | "drawio":
            return
        case _:
            print(f"Unknown file type {actual_suffix}", file=sys.stderr)
            print(f"File: {path}")
            print("" + 70 * "-")

    print()
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        print(
            f"Error: Cannot read file {path} as text. It may be binary or corrupted.",
            file=sys.stderr,
        )
        return

    print(text)
    print()
    print()

    print(f"{len(text)} bytes - {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
