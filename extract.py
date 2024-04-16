import os
from pathlib import Path, PureWindowsPath

import bs4

root = Path("/home/noebm/Downloads/kinect-firmware/KinectSDK-v1.8-Setup/")
file = root / "0"

soup = bs4.BeautifulSoup(open(file).read())

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
