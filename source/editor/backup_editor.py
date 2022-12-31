import copy
import json
import os.path
import time
import logging

import moviepy.editor as mp

import source.utils as utils


def backup_edit(
        video: mp.VideoFileClip, backup_file_path: str, output_path: str,
        suffix_path: str = None, suffix_last_part: str = None
):
    output_path = os.path.dirname(os.path.abspath(output_path))
    logging.info("Writing section parts to '{}'".format(output_path))

    logging.info("Locating section splits...")
    with open(backup_file_path) as f:
        lengths = json.loads(f.read())

    suffix_path_clip, suffix_last_part_clip = None, None

    if suffix_path is not None:
        logging.info("Reading video suffix '{}' into memory...".format(suffix_path))
        suffix_path_clip = mp.VideoFileClip(suffix_path)

    if suffix_last_part is not None:
        if suffix_path == suffix_last_part:
            suffix_last_part_clip = copy.copy(suffix_path_clip)

        else:
            logging.info("Reading video last part suffix '{}' into memory...".format(suffix_last_part))
            suffix_last_part_clip = mp.VideoFileClip(suffix_last_part)

    t = 0
    for i, length in enumerate(lengths):
        i += 1

        logging.info("Processing part {} ({})".format(i, utils.display_time(length)))
        segment: mp.VideoClip = video.subclip(t, t + length)

        if i != len(lengths):
            if suffix_path_clip is not None:
                logging.info("Appending video suffix to clip...")
                segment = mp.concatenate_videoclips([segment, copy.copy(suffix_path_clip)], method="compose")

        else:
            if suffix_last_part_clip is not None:
                logging.info("Appending last video prefix to clip...")
                segment = mp.concatenate_videoclips([segment, copy.copy(suffix_last_part_clip)], method="compose")

        logging.info(
            "Writing to disk as '{}'...".format(os.path.abspath(os.path.join(output_path, "Part{}.mp4".format(i))))
        )
        segment.write_videofile(
            os.path.join(output_path, "Part{}.mp4".format(i)),
            fps=video.fps,
            preset='ultrafast',
            codec='libx264',
            temp_audiofile=os.path.join('{}.m4a'.format(time.time())),
            remove_temp=True,
            audio_codec="aac",
            threads=6,
            verbose=False,
            # logger=None
        )

        t += length
