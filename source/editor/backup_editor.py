import json
import os.path
import time
import logging

import moviepy.editor as mp

import source.utils as utils


def backup_edit(video: mp.VideoFileClip, backup_file_path: str, output_path: str):
    output_path = os.path.dirname(os.path.abspath(output_path))
    logging.info("Writing section parts to '{}'".format(output_path))

    logging.info("Locating section splits...")
    with open(backup_file_path) as f:
        lengths = json.loads(f.read())

    t = 0
    for i, length in enumerate(lengths):
        i += 1

        logging.info("Processing part {} ({})".format(i, utils.display_time(length)))
        segment: mp.VideoClip = video.subclip(t, t + length)

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
