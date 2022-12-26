import os
import sys
import logging
import traceback

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

import source.ui as ui
import source.editor as editor

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="(%(asctime)s) <%(threadName)-10.10s> [%(levelname)-7.7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if pyi_splash is not None:
    pyi_splash.close()

if len(sys.argv) == 1:
    options = ui.show_gui()

    path_name = os.path.basename(os.path.normpath(options["output_path"]))

    try:
        duration = editor.edit_video(
            options["input_path"],
            os.path.join(options["output_path"], path_name),
            window_size=options["window_size"],
            volume_threshold=options["volume_threshold"],
            sound_pad=options["sound_pad"],
            section_length=float(options["segment_length"]) * 60,
            min_length_percent=options["min_length_percent"]
        )

        ui.show_completed(options["output_path"], duration)

    except Exception:
        traceback.print_exc()
        ui.show_completed(options["output_path"], None)

else:
    editor.edit_video(sys.argv[1], sys.argv[2], volume_threshold=0.01, section_length=25 * 60)
