# Copyright 2017 Alexandru Catrina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
FFMPEG wrapper
"""

from os import makedirs
from os.path import exists
from shutil import rmtree
from subprocess import Popen


DIR_SEPARATOR = r"/"
LOG_SDTOUT = "/tmp/nova/ffmpeg/log"


def create_path(output):
    dirs = output.split(DIR_SEPARATOR)
    filename = dirs.pop()
    filepath = DIR_SEPARATOR.join(dirs)
    if len(filepath) > 0 and not exists(filepath):
        makedirs(filepath)
    return output


def delete_temp(path):
    rmtree(path)
    return path


def create_cmd(fps, output, data):
    path, pattern = data.FRAME_PATH, data.FRAME_PATTERN
    frames = u"{}/{}".format(path, pattern.replace("{frame}", "%00d"))
    return ["ffmpeg", "-framerate", str(fps), "-i", frames,
        "-c:v", "libx264", "-profile:v", "high", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", u"{}".format(output)]


def ffmpeg(fps, output, nova):
    if output is None:
        raise ValueError("Missing output")
    create_path(output)
    create_path(LOG_SDTOUT)
    data = nova.recorder.Camera
    cmd = create_cmd(fps, output, data)
    code = None
    with open(LOG_SDTOUT, "wb") as log:
        proc = Popen(cmd, stdout=log, stderr=log)
        code = proc.wait()
        delete_temp(data.FRAME_PATH)
    return code
