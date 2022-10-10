import sys
import logging
import moviepy.editor as mp

import source.editor.backup_editor as backup_editor

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="(%(asctime)s) <%(threadName)-10.10s> [%(levelname)-7.7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("Reading file '{}' into memory...".format(sys.argv[1]))
video = mp.VideoFileClip(sys.argv[1])

backup_editor.backup_edit(video, sys.argv[2], sys.argv[3])
