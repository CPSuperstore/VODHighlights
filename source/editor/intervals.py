import math
import os.path
import time
import typing
import json
import source.typehints as typehints

import moviepy.editor as mp


def get_intervals_over_threshold(
        audio_clip: mp.AudioFileClip, window_size: float = 0.1, volume_threshold: float = 0.01, sound_pad: float = 0.25
) -> typehints.INTERVAL_TYPE:

    max_length = audio_clip.duration
    window_count = math.floor(audio_clip.end / window_size)

    intervals = []

    for i in range(window_count):
        start = i * window_size
        end = (i + 1) * window_size

        clip: mp.AudioFileClip = audio_clip.subclip(start, end)
        if clip.max_volume() >= volume_threshold:

            start -= sound_pad
            end += sound_pad

            start = max(start, 0)
            end = min(end, max_length)

            if len(intervals) == 0:
                intervals.append([start, end])

            else:
                if intervals[-1][1] >= start:
                    intervals[-1][1] = end

                else:
                    intervals.append([start, end])

    return intervals


def approximate_length(intervals: typehints.INTERVAL_TYPE) -> float:
    return sum(i[1] - i[0] for i in intervals)


def split_up_intervals(
        intervals: typehints.INTERVAL_TYPE, section_length: float = None, min_length_percent: float = 0.25
) -> typing.List[float]:

    lengths = [i[1] - i[0] for i in intervals]

    final_edit = []

    time_buffer = 0
    interval_buffer = []

    for interval, length in zip(intervals, lengths):
        time_buffer += length
        interval_buffer.append(interval)

        if time_buffer >= section_length:
            final_edit.append(interval_buffer)
            interval_buffer = []
            time_buffer = 0

    if len(interval_buffer) > 0:
        final_section_length = sum(s[1] - s[0] for s in interval_buffer)

        if final_section_length / section_length < min_length_percent:
            final_edit[-1].extend(interval_buffer)

        else:
            final_edit.append(interval_buffer)

    lengths = []
    for section in final_edit:
        lengths.append(sum(s[1] - s[0] for s in section))

    return lengths
