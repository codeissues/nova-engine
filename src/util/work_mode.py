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
Working mode wrapper.
"""

from __future__ import print_function

from time import sleep

from nova import Nova
from tools import nicefy
from reader import Reader
from recorder import Recorder
from webbrowser import WebBrowser
from user_agent import detect_engine, detect_browser

from core.events import Events
from core.schema import Schema
from core.worker import Worker
from core.javascript import JS

from libs.ffmpeg import ffmpeg


class WorkMode(Nova.Mode):

    display = Nova.Display.SystemScreen

    url, start_time, user_agent, environment = None, None, None, None
    nvs, browser, events, headless = None, None, None, False

    record, recorder = None, None

    def __init__(self, log, shell, headless=False, record=None):
        self.log = log
        self.log.info("Launching Nova in working mode...")
        self.shell = shell
        if headless:
            self.prepare_headless()
        if record is not None:
            self.prepare_camera()

    def prepare_headless(self):
        self.display = Nova.Display.VirtualScreen
        self.log.info("Notice: running headless in an X virtual framebuffer")
        return self

    def prepare_camera(self):
        self.record, self.recorder = True, Recorder
        self.log.info("Notice: recording session at {} FPS".format(self.shell.fps))
        return self

    def prepare_nvs(self):
        self.nvs = Reader(self.shell.task)
        self.log.info("Loading scenario from {}".format(self.shell.task))
        if self.nvs is None:
            raise TypeError("Unexpected null nova script")
        return self

    def prepare_headers(self):
        self.update_url().update_start_time().update_user_agent()
        self.update_environment()
        return self

    def prepare_events(self):
        self.events = {k:v for k, v in Events.builder(Schema)}
        return self

    def update_url(self):
        self.url = self.nvs.read()
        return self

    def update_start_time(self):
        self.start_time = self.nvs.read()
        return self

    def update_user_agent(self):
        self.user_agent = self.nvs.read()
        return self

    def update_environment(self):
        options = self.nvs.read()
        self.environment = options.split(",")
        return self

    def find_browser_by_user_agent(self):
        if self.shell.browser is not None:
            browser = self.shell.browser
            self.log.info("Overriding user agent with browser: {}".format(browser))
            return browser
        engine, browser = detect_engine(self.user_agent)
        return browser

    def start_browser(self):
        browser = self.find_browser_by_user_agent()
        WebBrowser.set_logger(self.log.info)
        self.browser = WebBrowser(browser, *self.environment[:2])
        self.browser.set_script(JS.ON_STARTUP)
        self.browser.open_page(self.url)
        return self

    def start_filming(self):
        @nicefy
        def _filming():
            Recorder.Camera.run(self.browser, self.log.info, self.shell)
        self.camera = Worker(_filming)
        self.camera.start()
        return self

    def start_activity(self):
        if self.record:
            self.start_filming()
        while not self.nvs.ended():
            action = self.nvs.read()
            if action is None:
                break
            try:
                event = self.read_event(action)
                self.browser.run_action(event)
            except Exception as e:
                self.log.warn("Recover event: {}".format(e))
        if self.record:
            self.camera.stop()
        self.browser.close_browser()
        return self

    def read_event(self, action):
        schema = Schema.developer(action)
        event = schema.pop("event", None)
        if event is None:
            raise ValueError("Outdated or invalid nvs: not able to decode event")
        event_class = self.events.get(event)
        if event_class is None or not callable(event_class):
            raise ValueError("Outdated or invalid nvs: not able to decode event")
        return event_class(schema)

    def run(self):
        self.prepare_nvs().prepare_headers().prepare_events()
        params = dict(zip(Nova.Display.PARAMS, self.environment[2:4]))
        with self.display(**params) as screen:
            self.start_browser().start_activity()
        self.log.info("Task done")

    def clean(self, callback=None, args=()):
        if callable(callback) and isinstance(args, tuple):
            try:
                reply = callback(*args)
                if reply is None:
                    reply = "n/a"
                self.log.info("Callback exitcode: {}".format(reply))
            except Exception as error:
                self.log.warn("Callback error: {}".format(error))
        self.log.info("Cleaning up...")


def work_mode(log, shell):
    Nova.work_mode(shell)
    try:
        opts = {}
        mode = WorkMode(log, shell, shell.headless, shell.record)
        if shell.record:
            opts.update({
                "callback": ffmpeg,
                "args": (shell.fps, shell.record, mode)
            })
        mode.run()
        mode.clean(**opts)
    except Exception as e:
        Nova.error(e)
