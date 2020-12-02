#!/usr/bin/env python
import os
import logging
import dvd_utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DVDs = [
    #    "Countdown To Christmas",
    "Blaafjelld1",
]

# This command freezes at the end of Episode 1 in Blaafjelld1
# ffmpeg -probesize 9G -analyzeduration 300M -fflags +genpts -i ts_01.vob -map 0 -map -0:d -c copy merged.mkv

for dvd in DVDs:
    path = os.path.join("output", dvd)
    video_ts = os.path.join(path, "VIDEO_TS")

    lsd = dvd_utils.lsdvd(video_ts)

    print(lsd)

    merged = dvd_utils.merge_vobs(video_ts, path)

    print(merged)

    split = dvd_utils.split_tracks(video_ts, merged, path)

    print(split)

    break
