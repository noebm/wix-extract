import os
import subprocess
import sys
from pathlib import Path, PureWindowsPath

import bs4

input_file = Path(sys.argv[1])

if not input_file.is_file():
    print("Input is not a file!")
    exit(1)

print(input_file)

root = Path(input_file.parent, input_file.stem)
print(root)
root.mkdir(exist_ok=True)

cmd = f"cabextract {input_file} -d {root}"
result = subprocess.run(cmd, shell=True)

if result.returncode != 0:
    print(f"'{cmd}' failed: {result.stdout}")

    exit(result.returncode)

index = root / "0"

with index.open() as f:
    soup = bs4.BeautifulSoup(f.read())

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
