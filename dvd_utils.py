#!/usr/bin/env python
import os
from ast import literal_eval
from os import PathLike
import subprocess
import logging
from typing import Dict, List
import json

logger = logging.getLogger(__name__)

BLOCK_SIZE = 4096 * 1024  # 4MB blocks
DVD_SECTOR_SIZE = 2048


def lsdvd(video_ts):
    res = subprocess.run(["lsdvd", "-x", "-Oy", video_ts], stdout=subprocess.PIPE, encoding="utf-8")
    try:
        data = literal_eval(res.stdout.split("lsdvd = ", 1)[-1])
    except:
        data = {}
        print(res.stdout)
    return data


#
def vob2mkv(vob_file: PathLike) -> PathLike:
    mkv_file = os.path.splitext(vob_file)[0] + ".mkv"
    subprocess.run(
        [
            "ffmpeg",
            "-probesize",
            "9G",
            "-analyzeduration",
            "300M",
            "-fflags",
            "+genpts",
            "-i",
            vob_file,
            "-map",
            "0",
            "-map",
            "-0:d",
            "-c",
            "copy",
            mkv_file,
        ]
    )

    return mkv_file


def encode(input_file, preset_file):
    with open(preset_file) as fh:
        preset = json.load(fh)
    preset_name = " ".join([x.get("PresetName") for x in preset.get("PresetList", [])]) or "encoded"

    input_fn = os.path.splitext(input_file)[0]
    output_file = f"{input_fn} - {preset_name}.mkv"
    subprocess.run(
        ["HandBrakeCLI", "--preset-import-file", preset_file, "--input", input_file, "--output", output_file]
    )
    return output_file


def find_vob(video_ts: str) -> Dict[int, List[Dict]]:
    results = {}
    for fn in sorted(os.listdir(video_ts)):
        fnu = fn.upper()
        name, ext = fnu.split(".", 1)
        if ext != "VOB":
            continue

        spl = name.split("_")

        if spl[0] == "VTS":
            title_set_id = int(spl[1])
            object_id = int(spl[2])

            # Video Object 0 is the menu for this Title
            if object_id == 0:
                continue

            if not title_set_id in results:
                results[title_set_id] = []

            results[title_set_id].append(
                {
                    "title_set": title_set_id,
                    "object": object_id,
                    "file": os.path.join(video_ts, fn),
                }
            )

    logger.debug(f"Located VOBs: {results}")

    return results


def merge_vobs(video_ts: str, output: str) -> Dict[int, str]:
    res = {}

    for title_set, objects in find_vob(video_ts).items():
        output_fn = os.path.join(output, f"ts_{title_set:02n}.vob")
        logger.info(f"Merging {len(objects)} object(s) of title set {title_set} into '{output_fn}'…")

        res[title_set] = output_fn

        with open(output_fn, "wb") as outfh:
            for obj in sorted(objects, key=lambda o: o["object"]):
                logger.debug(f"Reading title {title_set} object {obj['object']}: {obj['file']}…")

                with open(obj["file"], "rb") as infh:
                    while True:
                        data = infh.read(BLOCK_SIZE)
                        if not data:
                            break

                        outfh.write(data)
    return res


def split_tracks(video_ts, merged, output):

    lsd = lsdvd(video_ts)

    res = {}
    for track in lsd["track"]:
        print(track)
        title_set: int = track["vts"]
        track_id = track["ix"]
        logger.debug(f"Title {title_set} track {track_id}")

        output_fn = os.path.join(output, f"ts_{title_set:02n}_ch_{track_id:02n}.vob")

        with open(merged[title_set], "rb") as infh, open(output_fn, "wb") as outfh:
            for cell in track["cell"]:
                start = cell["first_sector"] * DVD_SECTOR_SIZE
                end = cell["last_sector"] * DVD_SECTOR_SIZE
                length = end - start

                infh.seek(start)

                logging.debug(
                    f"Track {track_id}, cell {cell['ix']}: copying {length} bytes from {merged[title_set]}:{start}-{end}"
                )
                transfer(infh, outfh, length)

        res[(title_set, track_id)] = output_fn

    return res


def transfer(infh, outfh, num):
    while num:
        b = min(BLOCK_SIZE, num)
        data = infh.read(b)
        outfh.write(data)
        num -= len(data)


def chapters2cells(chapters: List[Dict], cells: List[Dict]):
    _cells = {}
    for cell in cells:
        _cells[cell["ix"]] = cell

    _chapters = {}
    for _chapter in chapters:
        chapter = _chapter.copy()
        _chapters[chapter.pop("ix")] = chapter

    res = {}

    for ix, chapter in _chapters.items():
        x = []
        i = chapter["startcell"]
        while sum([y["length"] for y in x]) < chapter["length"]:
            x.append(_cells[i])
            i += 1
        res[ix] = x

    return res


if __name__ == "__main__":
    x = lsdvd("output/Blaafjelld1/VIDEO_TS")
    print(x)
