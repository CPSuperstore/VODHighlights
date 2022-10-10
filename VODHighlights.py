import sys
import logging

import source.editor as editor

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="(%(asctime)s) <%(threadName)-10.10s> [%(levelname)-7.7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

editor.edit_video(sys.argv[1], sys.argv[2], volume_threshold=0.01, section_length=25 * 60)
