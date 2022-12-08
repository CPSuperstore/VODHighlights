import json
import logging
import os
import shutil
import time

import moviepy.editor as mp

import source.editor.intervals as intervals
import source.editor.backup_editor as backup_editor
import source.utils as utils

BACKUP_DIR = "length_backups"
TEMP_DIR = "tmp"

if os.path.isdir(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)

os.makedirs(TEMP_DIR)

if not os.path.isdir(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)


def edit_video(
        input_path: str, output_path: str, window_size: float = 0.1, volume_threshold: float = 0.01,
        sound_pad: float = 0.25, section_length: float = None
) -> float:
    start = time.time()

    logging.info("Reading file '{}' into memory...".format(input_path))
    video = mp.VideoFileClip(input_path)

    logging.info("Initial video duration is {}".format(utils.display_time(video.duration)))

    logging.info("Locating intervals louder than {}%".format(round(volume_threshold * 100, 2)))
    interval = intervals.get_intervals_over_threshold(
        video.audio, window_size=window_size, volume_threshold=volume_threshold, sound_pad=sound_pad
    )

    estimated_length = intervals.approximate_length(interval)
    logging.info(
        "Located {} intervals. Estimated total duration: {}".format(
            len(interval), utils.display_time(estimated_length)
        )
    )

    if section_length is None:
        logging.info("Skipping section breakdown")

    else:
        logging.info("Breaking video into sections of length {}".format(utils.display_time(section_length)))
        broken_down_intervals = intervals.split_up_intervals(interval, section_length)

        for i, length in enumerate(broken_down_intervals):
            logging.info("    Section {} - {}".format(i + 1, utils.display_time(length)))

        backup_file = os.path.join(BACKUP_DIR, "{}.json".format(time.time()))

        logging.info("Backing up interval data to '{}'".format(os.path.abspath(backup_file)))

        with open(backup_file, 'w') as f:
            f.write(json.dumps(broken_down_intervals))

    logging.info("Writing full reel to disk (not split up. if requested, this will happen later)...")

    logging.info("Stitching {} segments back together... This will take a long time.".format(len(interval)))
    keep_clips = [video.subclip(max(start, 0), min(end, video.duration)) for [start, end] in interval]

    edited_video = mp.concatenate_videoclips(keep_clips)
    logging.info("Full edited duration is {}".format(utils.display_time(edited_video.duration)))

    filename = output_path if section_length is None else "{}_TMP.mp4".format(output_path)

    logging.info("Writing new video to '{}'... This will take a long time.".format(filename))
    edited_video.write_videofile(
        filename,
        fps=video.fps,
        preset='ultrafast',
        codec='libx264',
        temp_audiofile=os.path.join(TEMP_DIR, '{}.m4a'.format(time.time())),
        remove_temp=True,
        audio_codec="aac",
        threads=6,
        verbose=False,
        # logger=None
    )

    if section_length is not None:
        backup_editor.backup_edit(edited_video, backup_file, output_path)

        logging.info("Cleaning up temporary backup files...")
        os.remove(backup_file)
        os.remove(filename)

    logging.info("Edit completed. Took {}".format(utils.display_time(time.time() - start)))

    return time.time() - start
