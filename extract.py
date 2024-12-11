import argparse
import os
import subprocess
from pathlib import Path, PureWindowsPath

import bs4


def main():
    parser = argparse.ArgumentParser(
        # prog="wix-extract",
        description="A commandline utility for extracting wix installers",
    )

    parser.add_argument("-d", "--destination", help="storage destination")
    parser.add_argument("filename")

    args = parser.parse_args()

    input_file = Path(args.filename)

    if not input_file.is_file():
        print("Input is not a file!")
        exit(1)

    print(input_file)

    if args.destination:
        root = Path(args.destination)
    else:
        root = Path(input_file.stem)

    if not root.is_absolute():
        root = input_file.parent / root

    print(root)
    root.mkdir(exist_ok=True)

    cmd = ["cabextract", str(input_file), "-d", str(root)]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL)

    if result.returncode != 0:
        print(f"'{cmd}' failed: {result.stdout}")

        exit(result.returncode)

    index = root / "0"

    with index.open() as f:
        soup = bs4.BeautifulSoup(f.read(), features="lxml")

    os.remove(index)

    for payload in soup.find_all("payload"):
        maybe_filepath: str = payload.get("filepath")
        maybe_sourcepath: str = payload.get("sourcepath")
        # size = payload.get("size")
        # hash = payload.hash("hash")
        if not (maybe_filepath and maybe_sourcepath):
            continue

        filepath = PureWindowsPath(maybe_filepath)
        sourcepath = PureWindowsPath(maybe_sourcepath)

        assert not filepath.is_absolute()
        assert not sourcepath.is_absolute()

        output_path = Path(root, *filepath.parts)
        input_path = Path(root, *sourcepath.parts)

        if not input_path.exists():
            print(f"MISSING {input_path}")
            continue

        os.renames(input_path, output_path)


if __name__ == "__main__":
    main()
