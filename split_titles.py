#!/usr/bin/env python
import os
import logging
import dvd_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DVDs = [
    # "Blaafjelld1",
    # "Blaafjelld2",
    "Blaafjelld3",
]

for dvd in DVDs:
    path = os.path.join("output", dvd)
    video_ts = os.path.join(path, "VIDEO_TS")

    lsd = dvd_utils.lsdvd(video_ts)

    print(lsd)

    merged = dvd_utils.merge_vobs(video_ts, path)

    print(merged)

    split = dvd_utils.split_tracks(video_ts, merged, path)

    print(split)

    for (title_set, track_id), vob_file in split.items():
        mkv_file = dvd_utils.vob2mkv(vob_file)
        # Deinterlace works differently with CLI than the GUI? (same presets)
        # encoded = dvd_utils.encode(mkv_file, "presets/h264-2160p60.json")

    break
