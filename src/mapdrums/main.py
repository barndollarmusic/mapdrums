# SPDX-FileCopyrightText: 2022 Barndollar Music, Ltd.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import codecs
import csv
import jinja2
import pathlib
import re
import sys

__name__ = "mapdrums"
__version__ = "0.9.1"  # NOTE: Also update setup.cfg when updating version.

# Command-line arguments:
parser = argparse.ArgumentParser(
    prog=__name__,
    description="Generate Cubase Drum Map (.drm) files from input CSV")
parser.add_argument("input_csv", help="Input CSV file (Map, Key, Sound)")
parser.add_argument("--out_dir", nargs="?", default=".",
                    help="Directory to output .drm files to (defaults to current dir)")
parser.add_argument("--version", action="version", version=__version__)


# https://stackoverflow.com/questions/1546717/escaping-strings-for-use-in-xml
def xml_escape(input: str) -> str:
    result = input.replace("&", "&amp;")  # First, to avoid escaping & further.
    result = result.replace("<", "&lt;")
    result = result.replace(">", "&gt;")
    result = result.replace("\"", "&quot;")
    return result


class DrumMap:
    """Data for an individual drum map."""
    name: str
    keys: dict[int, str]
    sorted_keys = range(128)

    def __init__(self, name: str) -> None:
        self.name = name
        self.keys = {}

    def is_mapped(self, key: int) -> bool:
        """Returns True if key is mapped."""
        return key in self.keys

    def sound(self, key: int) -> str:
        """Returns XML value escaped sound or '---' if unmapped."""
        return "---" if key not in self.keys else xml_escape(self.keys[key])


def fatal(msg: str) -> None:
    """Prints msg and exits program with an error status."""
    sys.exit(f"[{__name__}] {msg}")


SAFE_FILENAME = re.compile("^[\w\-., ]+$")


def validate_row(row: dict[str, str], row_number: int) -> None:
    """Validates an input CSV row."""
    # Requires Map, Key, and Sound columns.
    if "Map" not in row or row["Map"] is None:
        fatal(f"Row {row_number}: 'Map' column is required")
    elif "Key" not in row or row["Key"] is None:
        fatal(f"Row {row_number}: 'Key' column is required")
    elif "Sound" not in row or row["Sound"] is None:
        fatal(f"Row {row_number}: 'Sound' column is required")
    
    # Map must be a valid filename.
    map_name = row["Map"]
    if not SAFE_FILENAME.fullmatch(map_name):
        fatal(f"Row {row_number}: 'Map' column value is not a safe filename: '{map_name}'")
    
    # Key must be a 0-127 MIDI key number.
    key_str = row["Key"]
    try:
        key = int(key_str)
    except ValueError:
        fatal(f"Row {row_number}: 'Key' column value is not an integer: '{key_str}'")
    if key < 0 or 127 < key:
        fatal(f"Row {row_number}: 'Key' column value must be in [0, 127] range: '{key_str}'")
    
    # Sound must be a non-empty string.
    sound_str = row["Sound"]
    if len(sound_str) == 0 or sound_str.isspace():
        fatal(f"Row {row_number}: 'Sound' column value is empty")


def cli():
    """Command-line interface."""
    args = parser.parse_args()

    # Ensure output dir exists.
    out_dir = pathlib.Path(args.out_dir).resolve()
    if not out_dir.exists():
        fatal(f"--out_dir does NOT exist: '{out_dir}'")
    elif not out_dir.is_dir():
        fatal(f"--out_dir is NOT a directory: '{out_dir}'")

    # Read input CSV data.
    maps: dict[str, DrumMap] = {}
    with open(args.input_csv, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        row_number = 1
        for row in reader:
            row_number += 1
            validate_row(row, row_number)

            map_name = row["Map"]
            if map_name not in maps:
                maps[map_name] = DrumMap(map_name)
            maps[map_name].keys[int(row["Key"])] = row["Sound"]
    
    # Output drum maps.
    module_dir = pathlib.Path(__file__).parent.absolute()
    loader = jinja2.FileSystemLoader(module_dir / "data")
    env = jinja2.Environment(loader=loader)
    env.trim_blocks = True
    env.lstrip_blocks = True
    template = env.get_template("template.drm")

    for map_name in maps:
        out = template.render({"map": maps[map_name]})

        drm_filename = out_dir / f"{map_name}.drm"
        with codecs.open(drm_filename, "w", "utf-8") as drm_file:
            drm_file.write(out)
        
        print(f"[{__name__}] Wrote {drm_filename}")
