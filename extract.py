import argparse
import logging
import subprocess
from pathlib import Path, PureWindowsPath
from typing import List, Tuple

import bs4


class ExtractionError(Exception):
    pass


def extract_wix_installer(input_file: Path, destination: Path | None = None) -> Path:
    """
    Extract a WiX installer using cabextract.
    """
    if not input_file.is_file():
        raise ExtractionError(f"Input is not a file: {input_file}")

    root = destination or input_file.parent / input_file.stem
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    cmd = ["cabextract", str(input_file), "-d", str(root)]

    try:
        subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return root

    except subprocess.CalledProcessError as e:
        raise ExtractionError(f"Extraction failed: {e.stderr}")


class ProcessingError(Exception):
    pass


def remap_archive_path(archivepath: Path, root: Path) -> Path:
    """
    Remap an archive path to an absolute path within the root directory.
    """
    if archivepath.is_absolute():
        raise ValueError(f"Archive path cannot be absolute: {archivepath}")
    return root / archivepath


def archive_paths(archive_index: Path) -> List[Tuple[Path, Path]]:
    """
    Extract archive paths mapped to filepaths from the archive XML.
    """
    try:
        with archive_index.open("r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f.read(), features="lxml")

        def windows_to_posix_path(windowspath: str) -> Path:
            return Path(PureWindowsPath(windowspath).as_posix())

        paths = [
            (
                windows_to_posix_path(payload.get("sourcepath", "")),
                windows_to_posix_path(payload.get("filepath", "")),
            )
            for payload in soup.find_all("payload")
        ]

        if not paths:
            raise ProcessingError(f"No payload paths found in the archive index")

        return paths

    except IOError as e:
        raise ProcessingError(f"Error parsing archive index: {e}")


def process_archives(root: Path):
    """
    Process archive paths and rename files accordingly.
    """
    index = root / "0"

    if not index.exists():
        raise ProcessingError(f"Index file not found: {index}")

    try:
        for archivepath, filepath in archive_paths(index):
            input_path = remap_archive_path(archivepath, root)
            output_path = remap_archive_path(filepath, root)

            if not input_path.exists():
                logging.warning(f"Missing input path: {input_path}")
                continue

            input_path.rename(output_path)

        index.unlink()

    except Exception as e:
        raise ProcessingError(f"Error processing archives: {e}")


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(
        description="A command-line utility for extracting WiX installers"
    )
    parser.add_argument("-d", "--destination", type=Path, help="Storage destination")
    parser.add_argument("filename", type=Path, help="Path to the installer file")

    args = parser.parse_args()

    try:

        root = extract_wix_installer(args.filename, args.destination)
        process_archives(root)
        logging.info(f"Successfully extracted and processed: {args.filename}")

    except ExtractionError as e:
        logging.error(f"Extraction failed: {e}")
        exit(1)

    except ProcessingError as e:
        logging.error(f"Processing failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
