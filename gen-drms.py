#!/usr/bin/env python3

import argparse
import codecs
import csv
import jinja2

# Command-line arguments:
parser = argparse.ArgumentParser(
    prog="gen-drms",
    description="Generate Cubase Drum Map (.drm) files from input CSV")
parser.add_argument("input_csv", help="Input CSV file (Map, Key, Sound)")


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


def cli():
    """Command-line interface."""
    args = parser.parse_args()

    # Read input CSV data.
    maps: dict[str, DrumMap] = {}
    with open(args.input_csv, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            map_name = row["Map"]
            if map_name not in maps:
                maps[map_name] = DrumMap(map_name)
            maps[map_name].keys[int(row["Key"])] = row["Sound"]
    
    # Output drum maps.
    loader = jinja2.FileSystemLoader("templates")
    env = jinja2.Environment(loader=loader)
    env.trim_blocks = True
    env.lstrip_blocks = True
    template = env.get_template("template.drm")

    for map_name in maps:
        out = template.render({"map": maps[map_name]})

        # TODO: Ensure safe filename.
        drm_filename = f"{map_name}.drm"
        with codecs.open(drm_filename, "w", "utf-8") as drm_file:
            drm_file.write(out)
        
        print(f"Wrote {drm_filename}")


if __name__ == "__main__":
    cli()
