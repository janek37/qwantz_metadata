# Dinosaur Comic Metadata Processor

A set of tools for collecting various [Ryan North](https://www.ryannorth.ca/)'s [Dinosaur Comics](https://qwantz.com) metadata and compiling them into one JSON document.

It uses transcripts obtained using my other project, https://github.com/janek37/parse_qwantz.

## Installation

Install `qwantz-metadata` with `pip`

```bash
  pip install qwantz-metadata
```

## Usage

You need three directories: one containing the comic transcripts, one containing the footer transcripts, and one containing raw HTML files.

The transcripts and footers are required to be plain text files with filenames like `<comic_id> - <image_filename>.txt`, e.g. `0001 - comic2-02.png.txt`.

The filenames of the HTML files are not relevant.

Once the directories are ready, run `qwantz-metadata` to print the combined metadata JSON document to the standard output:

```
$ qwantz-metadata <transcript_dir> <footer_dir> <html_dir> > output.json
```

## Acknowledgments

This program would not be possible without the wonderful comics by Ryan North!
