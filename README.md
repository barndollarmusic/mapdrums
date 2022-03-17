# cubase-drum-maps
Generate Cubase Drum Map (.drm) files from input CSV

## Usage

See [`SampleInput.csv`](SampleInput.csv) for format of the input data. You can
edit it and save a `.csv` file using Google Sheets or Excel.

Feel free to add additional columns, but this script requires `Map` (drum map
name), `Key` (MIDI key number), and `Sound` (label for the sound that key
makes). As in the sample, you can create multiple drum maps from a single input
`.csv` file.

Prereqs:
- [Python3](https://www.python.org/downloads/)
- Jinja2 library (see below)

```bash
pip install Jinja2
```

Then run:
```bash
python3 gen-drms.py YourInput.csv
```

This will output one `.drm` file for every unique `Map` value in your CSV data.
