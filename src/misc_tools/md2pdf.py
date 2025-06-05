import subprocess
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    for arg in args:
        path = Path(arg)
        if not path.is_file():
            print(f"Error: {path} is not a file.", file=sys.stderr)
            continue
        if path.suffix != ".md":
            print(f"Error: {path} is not a markdown file.", file=sys.stderr)
            continue
        pdf_path = path.with_suffix(".pdf")

        # args: pandoc -o docs.pdf -t html docs.md
        args = ["pandoc", "-o", str(pdf_path), "-t", "html", str(path)]
        subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
