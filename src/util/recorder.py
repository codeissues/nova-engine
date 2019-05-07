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
Video record capabilities to monitor browser interactivity.
"""

from os import path, makedirs
from time import sleep


class Recorder(object):

    class Camera(object):

        WAIT_TIME = .1
        FRAME_PATH, FRAME_PATTERN = r"/tmp/nova/temp", r"frame-{frame}.png"

        def __init__(self, app, log, args):
            self.app, self.log, self.args = app, log, args
            self.initialize()

        @classmethod
        def run(cls, app, log, args):
            cam = cls(app, log, args)
            cam.record()
            return cls

        def initialize(self):
            self.browser = self.app.browser
            self.frame = 1
            self.fps = 1. / int(self.args.fps)
            if not path.exists(self.FRAME_PATH):
                makedirs(self.FRAME_PATH)

        def record(self):
            while not self.app.ready():
                sleep(self.WAIT_TIME)
            self.log("Page ready. Recording...")
            while not self.app.closed:
                self.capture() and sleep(self.fps)

        def capture(self):
            frame_name = self.FRAME_PATTERN.format(frame=self.frame)
            frame_path = u"{}/{}".format(self.FRAME_PATH, frame_name)
            self.browser.save_screenshot(frame_path)
            self.frame += 1
            return True
