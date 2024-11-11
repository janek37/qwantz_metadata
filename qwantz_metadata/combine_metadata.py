import dataclasses
import json
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path
from typing import NamedTuple, IO

import typer

import qwantz_metadata
from qwantz_metadata.parse_qwantz_html import MetadataFromHTML, parse_qwantz_html, BASE_URL

app = typer.Typer()

IMAGE_URL_PREFIX = BASE_URL + "/comics/"

EXTRA_METADATA_PATH = files(qwantz_metadata).joinpath('data/extra_metadata.json')
GUEST_COMICS_PATH = files(qwantz_metadata).joinpath('data/guest_comics.json')
SPECIAL_COMICS_PATH = files(qwantz_metadata).joinpath('data/special_comics.json')


class ExtraMetadata(NamedTuple):
    comic_id: int
    image_url: str
    panels: list[list[str]] | None = None
    description: str | None = None
    guest_artist: str | None = None
    guest_artist_url: str | None = None
    header_texts: list[str] | None = None
    footer: list[str] | None = None


@dataclass
class CombinedMetadata:
    comic_id: int
    comic_url: str
    date: str
    image_url: str
    title_text: str
    contact_text: str
    archive_text: str
    haps: str | None
    header_texts: list[str]
    image_link_target: str | None
    panels: list[list[str]] | None = None
    description: str | None = None
    guest_artist: str | None = None
    guest_artist_url: str | None = None
    footer: list[str] | None = None

    @classmethod
    def from_html_metadata(cls, html_metadata: MetadataFromHTML) -> "CombinedMetadata":
        kwargs = html_metadata._asdict()
        comic_date = kwargs.pop("date").isoformat()
        return cls(date=comic_date, **kwargs)

    def apply_extra(self, extra_metadata: ExtraMetadata) -> None:
        for key, value in extra_metadata._asdict().items():
            if value is not None:
                setattr(self, key, value)


@app.command()
def combine_metadata_command(transcripts_dir: Path, footers_dir: Path, html_dir: Path) -> None:
    combine_metadata(transcripts_dir, footers_dir, html_dir, sys.stdout)


def combine_metadata(transcripts_dir: Path, footers_dir: Path, html_dir: Path, output_file: IO[str]) -> None:
    extra_metadata_by_url = {md.image_url: md for md in load_metadata(EXTRA_METADATA_PATH)}
    guest_comics_by_url = {md.image_url: md for md in load_metadata(GUEST_COMICS_PATH)}
    special_comics_by_url = {md.image_url: md for md in load_metadata(SPECIAL_COMICS_PATH)}

    transcripts_by_url = {image_url: panels for image_url, panels in get_transcripts(transcripts_dir)}
    footers_by_url = {image_url: footer for image_url, footer in get_footers(footers_dir)}

    result = []
    for html_metadata in get_metadata_from_html(html_dir):
        image_url = html_metadata.image_url
        combined = CombinedMetadata.from_html_metadata(html_metadata)
        if image_url in transcripts_by_url:
            combined.panels = transcripts_by_url[image_url]
        if image_url in footers_by_url:
            combined.footer = footers_by_url[image_url]
        if image_url in extra_metadata_by_url:
            combined.apply_extra(extra_metadata_by_url[image_url])
        if image_url in special_comics_by_url:
            combined.apply_extra(special_comics_by_url[image_url])
        if image_url in guest_comics_by_url:
            combined.apply_extra(guest_comics_by_url[image_url])
        result.append(dataclasses.asdict(combined))

    json.dump(result, output_file, indent=2, ensure_ascii=False)


def get_transcripts(transcripts_dir: Path) -> Iterator[tuple[str, list[list[str]]]]:
    for trancript_file_path in transcripts_dir.iterdir():
        if trancript_file_path.is_file() and trancript_file_path.suffix == ".txt":
            base_name = trancript_file_path.stem
            _, image_filename = base_name.split(" - ")
            image_url = IMAGE_URL_PREFIX + image_filename
            panels = get_panels(trancript_file_path.open())
            yield image_url, panels


def get_footers(footers_dir: Path) -> Iterator[tuple[str, list[str]]]:
    for footer_file_path in footers_dir.iterdir():
        if footer_file_path.is_file() and footer_file_path.suffix == ".txt":
            base_name = footer_file_path.stem
            _, image_filename = base_name.split(" - ")
            image_url = IMAGE_URL_PREFIX + image_filename
            footer = [line.rstrip() for line in footer_file_path.open()]
            yield image_url, footer


def get_metadata_from_html(html_dir: Path) -> Iterator[MetadataFromHTML]:
    for html_file_path in sorted(html_dir.iterdir()):
        html = html_file_path.open().read()
        yield from parse_qwantz_html(html)


def get_panels(lines: Iterable[str]) -> list[list[str]]:
    panels = []
    current_panel = []
    for line in lines:
        line = line.rstrip()
        if not line:
            panels.append(current_panel)
            current_panel = []
        else:
            current_panel.append(line)
    if current_panel:
        panels.append(current_panel)
    return panels


def load_metadata(json_path: Traversable) -> Iterator[ExtraMetadata]:
    for image_path, metadata_dict in json.load(json_path.open()).items():
        yield ExtraMetadata(
            comic_id=metadata_dict["comic_id"],
            image_url=IMAGE_URL_PREFIX + image_path,
            panels=metadata_dict.get("panels"),
            description=metadata_dict.get("description"),
            guest_artist=metadata_dict.get("guest_artist"),
            guest_artist_url=metadata_dict.get("guest_artist_url"),
            header_texts=metadata_dict.get("header_texts"),
            footer=metadata_dict.get("footer"),
        )


if __name__ == '__main__':
    app()
