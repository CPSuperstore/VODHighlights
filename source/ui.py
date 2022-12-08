import datetime
import json

import PySimpleGUI as sg
import os
import sys

WINDOW_SETTINGS = {
    "title": "Stream Highlight Creator",
    "finalize": True,
    "icon": "assets/logo.ico" if os.name == 'nt' else "assets/logo.png"
}

sg.change_look_and_feel('Dark2')

VIDEO_FORMATS = [".ogv", ".mp4", ".mpeg", ".avi", ".mov"]
FILE_TYPES = (("Video Files", "*.ogv *.mp4 *.mpeg *.avi *.mov"),)

INPUT_PATH = ""
OUTPUT_PATH = ""
VIDEO_PREFIX = "Part_"
FILE_TYPE = ".mp4"
WINDOW_SIZE = 0.1
VOLUME_THRESHOLD = 1
SOUND_PAD = 0.25
SEGMENT_LENGTH = "25"

DEFAULTS_FILE = "defaults.json"


def get_layout() -> list:
    label_width = 25
    slider_width = 35
    slider_height = 20

    return [
        [sg.Text("Stream Highlight Creator", justification='center')],
        [
            sg.Text("Input File", size=(label_width, None), justification='right'),
            sg.Input(key="input_path", default_text=INPUT_PATH),
            sg.FileBrowse(button_text="Browse...", file_types=FILE_TYPES)
        ],
        [
            sg.Text("Output Directory", size=(label_width, None), justification='right'),
            sg.Input(key="output_path", default_text=OUTPUT_PATH),
            sg.FolderBrowse(button_text="Browse...")
        ],
        [
            sg.Text("Video Segment Length (Minutes)", size=(label_width, None), justification='right'),
            sg.Input(key="segment_length", default_text=SEGMENT_LENGTH),
        ],
        # [
        #     sg.Text("Name Prefix", size=(label_width, None), justification='right'),
        #     sg.Input(key="name_prefix", default_text=VIDEO_PREFIX),
        #     sg.FolderBrowse(button_text="Save As...")
        # ],
        [
            sg.Text("Output Format", size=(label_width, None), justification='right'),
            sg.Combo(
                VIDEO_FORMATS, readonly=True, default_value=FILE_TYPE, key="file_format", size=(slider_width + 8, None)
            )
        ],
        [
            sg.Text("Sound Pad", size=(label_width, None), justification='right'),
            sg.Slider(
                (0, 1), default_value=SOUND_PAD, resolution=0.05, orientation="h", key="sound_pad",
                size=(slider_width, slider_height)
            )
        ],
        [
            sg.Text("Window Size", size=(label_width, None), justification='right'),
            sg.Slider(
                (0.1, 5), default_value=WINDOW_SIZE, resolution=0.1, orientation="h", key="window_size",
                size=(slider_width, slider_height)
            )
        ],
        [
            sg.Text("Volume Threshold", size=(label_width, None), justification='right'),
            sg.Slider(
                (0, 100), default_value=VOLUME_THRESHOLD, resolution=1, orientation="h", key="volume_threshold",
                size=(slider_width, slider_height)
            )
        ],
        [sg.Button("Start")]
    ]


def show_gui():
    global INPUT_PATH
    global OUTPUT_PATH
    global WINDOW_SIZE
    global VOLUME_THRESHOLD
    global SOUND_PAD
    global VIDEO_PREFIX
    global FILE_TYPE
    global SEGMENT_LENGTH

    try:
        with open(DEFAULTS_FILE, 'r') as f:
            defaults = json.loads(f.read())

            INPUT_PATH = defaults.get("input_path", INPUT_PATH)
            OUTPUT_PATH = defaults.get("output_path", OUTPUT_PATH)

            # VIDEO_PREFIX = defaults["name_prefix"]
            SEGMENT_LENGTH = defaults.get("segment_length", SEGMENT_LENGTH)
            FILE_TYPE = defaults.get("file_format", FILE_TYPE)
            WINDOW_SIZE = defaults.get("window_size", WINDOW_SIZE)
            VOLUME_THRESHOLD = defaults.get("volume_threshold", VOLUME_THRESHOLD)
            SOUND_PAD = defaults.get("sound_pad", SOUND_PAD)

    except (FileNotFoundError, json.JSONDecodeError):
        pass

    window = sg.Window(layout=get_layout(), **WINDOW_SETTINGS)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            sys.exit(0)

        if event == "Start":
            if values["input_path"].replace(" ", "") == "":
                validation_error("You must specify the input path")

            elif values["output_path"].replace(" ", "") == "":
                validation_error("You must specify the output path")
            #
            # elif values["name_prefix"].replace(" ", "") == "":
            #     validation_error("You must specify the file name prefix")

            elif values["output_path"].replace(" ", "") == values["input_path"].replace(" ", ""):
                validation_error("Input and output paths must be different")

            else:
                SEGMENT_LENGTH = values["segment_length"]
                INPUT_PATH = values["input_path"]
                OUTPUT_PATH = values["output_path"]
                # VIDEO_PREFIX = values["name_prefix"]
                FILE_TYPE = values["file_format"]

                WINDOW_SIZE = values["window_size"]
                VOLUME_THRESHOLD = values["volume_threshold"]
                SOUND_PAD = values["sound_pad"]

                window.close()

                result = dict(
                    input_path=values["input_path"],
                    output_path=values["output_path"],
                    window_size=values["window_size"],
                    # name_prefix=values["name_prefix"],
                    file_format=values["file_format"],
                    volume_threshold=values["volume_threshold"] / 100,
                    sound_pad=values["sound_pad"],
                    segment_length=values["segment_length"]
                )

                with open(DEFAULTS_FILE, 'w') as f:
                    f.write(json.dumps(result))

                return result


def show_completed(output_path: str, duration: float):
    settings = WINDOW_SETTINGS.copy()
    del settings["finalize"]

    if duration is None:
        sg.popup(
            "Export Failed",
            "There is no point in the video which is louder than the volume threshold\n"
            "Please reduce the threshold and try again!",
            **settings
        )
        return

    sg.popup(
        "Edit Complete",
        "Highlight reel has been created and saved to '{}'\n\nTook {}\n\nHave a nice day :)".format(
            output_path, str(datetime.timedelta(seconds=duration)).split(".")[0],
        ),
        **settings
    )


def validation_error(message: str):
    settings = WINDOW_SETTINGS.copy()
    del settings["finalize"]

    sg.popup(
        "Validation Error", message, **settings
    )


def show_error(file_path: str):
    settings = WINDOW_SETTINGS.copy()
    del settings["finalize"]

    sg.popup(
        "Something Went Wrong",
        "Stream Highlight Creator encountered an error.\n\nPlease send dump file to Chris with dump file at {}".format(
            file_path
        ),
        **settings
    )
