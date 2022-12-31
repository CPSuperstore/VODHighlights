import datetime
import json
import sys

import PySimpleGUI as sg

import source.update_checker as update_checker
import source.ui_defaults as ui_defaults

sg.change_look_and_feel('Dark2')

VIDEO_FORMATS = [".ogv", ".mp4", ".mpeg", ".avi", ".mov"]
FILE_TYPES = (("Video Files", "*.ogv *.mp4 *.mpeg *.avi *.mov"),)

INPUT_PATH = ""
OUTPUT_PATH = ""
VIDEO_PREFIX = "Part_"
FILE_TYPE = ".mp4"
WINDOW_SIZE = 0.1
VOLUME_THRESHOLD = 0.01
SOUND_PAD = 0.25
SEGMENT_LENGTH = "25"
MIN_LENGTH_PERCENT = 0.25

VIDEO_SUFFIX = ""
LAST_PART_SAME_AS_REST = True
LAST_PART_SUFFIX = ""

DEFAULTS_FILE = "defaults.json"


def get_layout() -> list:
    label_width = 25
    slider_width = 35
    slider_height = 20

    video_suffix_last_part_state = LAST_PART_SAME_AS_REST

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
        [
            sg.Text("Min Length Percent", size=(label_width, None), justification='right'),
            sg.Slider(
                (0, 100), default_value=MIN_LENGTH_PERCENT, resolution=1, orientation="h", key="min_length_percent",
                size=(slider_width, slider_height)
            )
        ],
        [
            sg.Text("Video Suffix", size=(label_width, None), justification='right'),
            sg.Input(key="video_suffix", default_text=VIDEO_SUFFIX),
            sg.FileBrowse(button_text="Browse...", file_types=FILE_TYPES)
        ],
        [
            sg.Text("Last Part Is Same As Rest", size=(label_width, None), justification='right'),
            sg.Checkbox(key="video_suffix_same_as_rest", default=LAST_PART_SAME_AS_REST, text="", enable_events=True)
        ],
        [
            sg.Text("Video Suffix Of Last Part", size=(label_width, None), justification='right'),
            sg.Input(
                key="video_suffix_last_part", default_text=LAST_PART_SUFFIX, disabled=video_suffix_last_part_state
            ),
            sg.FileBrowse(
                button_text="Browse...", file_types=FILE_TYPES, key="video_suffix_last_part_button",
                disabled=video_suffix_last_part_state
            )
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
    global MIN_LENGTH_PERCENT
    global VIDEO_SUFFIX
    global LAST_PART_SAME_AS_REST
    global LAST_PART_SUFFIX

    try:
        with open(DEFAULTS_FILE, 'r') as f:
            defaults = json.loads(f.read())

            INPUT_PATH = defaults.get("input_path", INPUT_PATH)
            OUTPUT_PATH = defaults.get("output_path", OUTPUT_PATH)

            # VIDEO_PREFIX = defaults["name_prefix"]
            SEGMENT_LENGTH = defaults.get("segment_length", SEGMENT_LENGTH)
            FILE_TYPE = defaults.get("file_format", FILE_TYPE)
            WINDOW_SIZE = defaults.get("window_size", WINDOW_SIZE)
            VOLUME_THRESHOLD = defaults.get("volume_threshold", VOLUME_THRESHOLD) * 100
            SOUND_PAD = defaults.get("sound_pad", SOUND_PAD)
            MIN_LENGTH_PERCENT = defaults.get("min_length_percent", MIN_LENGTH_PERCENT) * 100

            VIDEO_SUFFIX = defaults.get("video_suffix", VIDEO_SUFFIX)
            LAST_PART_SAME_AS_REST = defaults.get("video_suffix_same_as_rest", LAST_PART_SAME_AS_REST)

            if LAST_PART_SAME_AS_REST:
                LAST_PART_SUFFIX = ""
            else:
                LAST_PART_SUFFIX = defaults.get("video_suffix_last_part", LAST_PART_SUFFIX)

    except (FileNotFoundError, json.JSONDecodeError):
        pass

    window = sg.Window(layout=get_layout(), **ui_defaults.WINDOW_SETTINGS)
    state = update_checker.is_update_pending()
    if state is not False:
        update_checker.show(state)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            sys.exit(0)

        if event == "video_suffix_same_as_rest":
            state = 'disabled' if values["video_suffix_same_as_rest"] else "normal"

            window["video_suffix_last_part"].Widget.configure(state=state)
            window["video_suffix_last_part_button"].Widget.configure(state=state)

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

                VIDEO_SUFFIX = values["video_suffix"]
                LAST_PART_SAME_AS_REST = values["video_suffix_same_as_rest"]
                LAST_PART_SUFFIX = values["video_suffix_last_part"]

                window.close()

                video_suffix = values["video_suffix"]
                video_suffix_same_as_rest = values["video_suffix_same_as_rest"]
                video_suffix_last_part = values["video_suffix_last_part"]

                if video_suffix_same_as_rest:
                    video_suffix_last_part = video_suffix

                if video_suffix.strip() == "":
                    video_suffix = None

                if video_suffix_last_part.strip() == "":
                    video_suffix_last_part = None

                result = dict(
                    input_path=values["input_path"],
                    output_path=values["output_path"],
                    window_size=values["window_size"],
                    # name_prefix=values["name_prefix"],
                    file_format=values["file_format"],
                    volume_threshold=values["volume_threshold"] / 100,
                    sound_pad=values["sound_pad"],
                    segment_length=values["segment_length"],
                    min_length_percent=values["min_length_percent"] / 100,
                    video_suffix=video_suffix,
                    video_suffix_same_as_rest=video_suffix_same_as_rest,
                    video_suffix_last_part=video_suffix_last_part
                )

                with open(DEFAULTS_FILE, 'w') as f:
                    f.write(json.dumps(result))

                return result


def show_completed(output_path: str, duration: float):
    settings = ui_defaults.WINDOW_SETTINGS.copy()
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
    settings = ui_defaults.WINDOW_SETTINGS.copy()
    del settings["finalize"]

    sg.popup(
        "Validation Error", message, **settings
    )


def show_error(file_path: str):
    settings = ui_defaults.WINDOW_SETTINGS.copy()
    del settings["finalize"]

    sg.popup(
        "Something Went Wrong",
        "Stream Highlight Creator encountered an error.\n\nPlease send dump file to Chris with dump file at {}".format(
            file_path
        ),
        **settings
    )
