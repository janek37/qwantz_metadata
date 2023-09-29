#!/usr/bin/env python3
import json
from pathlib import Path

import typer

app = typer.Typer()


def add_extra_metadata(json_path: Path, image_path: Path) -> None:
    extras = json.load(json_path.open())
    comic_id, file_name = image_path.name.split(' - ')
    if file_name not in extras:
        comic_id, file_name = image_path.name.split(' - ')
        extras[file_name] = {"comic_id": int(comic_id)}
    extras = {key: value for key, value in sorted(extras.items(), key=lambda r: r[1]["comic_id"])}
    json.dump(extras, json_path.open('w'), indent=2, ensure_ascii=False)


if __name__ == '__main__':
    typer.run(add_extra_metadata)
