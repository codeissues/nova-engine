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
Interactive mode wrapper.
"""

from __future__ import print_function

from nova import Nova
from webbrowser import WebBrowser

from core.events import Events
from core.schema import Schema


class InteractiveMode(Nova.Mode):

    EXIT, REPL, EVAL = r"=exit", r"_", r"="

    last_repl = None

    display = Nova.Display.VirtualScreen
    resolution, default_resolution = None, [800, 600]

    events = None

    def __init__(self, log, shell):
        self.log = log
        self.log.info("Launching Nova in interactive mode...")
        self.shell = shell

    def prepare_display(self):
        if not self.shell.resolution:
            self.resolution = self.default_resolution
            return self
        self.resolution = map(int, self.shell.resolution.split(r"x"))
        if len(self.resolution) != len(self.default_resolution):
            self.resolution = self.default_resolution
        return self

    def prepare_events(self):
        self.events = {k:v for k, v in Events.builder(Schema)}
        return self

    def start_browser(self):
        WebBrowser.set_logger(self.log.info)
        self.browser = WebBrowser(self.shell.browser, *self.resolution)
        if self.shell.starturl:
            self.browser.open_page(self.shell.starturl)
        return self

    def start_repl(self):
        self.log.info("""Loading REPL...
    * Type any javascript code and it will be executed with the selected browser
    * Use return statement to read an evaluated value; e.g. var a = 2; return a;
    * Type an equal sign to evaluate specific nova code such as events
    * The last stored value is accessible through underscore sign
    * You can exit anytime with ^C or '{}'
        """.format(self.EXIT))
        while True:
            try:
                stdin = raw_input(">>> ")
                if stdin == self.EXIT:
                    break
                if stdin.startswith(self.EVAL):
                    try:
                        event = self.test_event(stdin[1:].lstrip())
                        self.value(event._setter)
                    except Exception as e:
                        self.error(e)
                elif stdin == self.REPL:
                    self.value()
                else:
                    self.test(stdin)
            except KeyboardInterrupt:
                print("") # force new line
                break
        self.log.info("Closing REPL...")

    def value(self, value=None):
        if value is None:
            value = self.last_repl
        print("OUT => {}\n".format(value))

    def error(self, error):
        print("ERR => {}\n".format(error))

    def test(self, stdin):
        try:
            self.last_repl = self.browser.run_js(stdin)
            self.value(self.last_repl)
        except Exception as e:
            self.error(e)
        return self.last_repl

    def test_event(self, action):
        schema = Schema.developer(action)
        event = schema.pop("event", None)
        if event is None:
            raise ValueError("Outdated or invalid nvs: not able to decode event")
        event_class = self.events.get(event)
        if event_class is None or not callable(event_class):
            raise ValueError("Outdated or invalid nvs: not able to decode event")
        return event_class(schema)

    def run(self):
        self.prepare_display().prepare_events()
        params = dict(zip(Nova.Display.PARAMS, self.resolution + [24]))
        with self.display(**params) as screen:
            self.start_browser().start_repl()

    def clean(self):
        try:
            self.browser.close_browser()
        except Exception as e:
            self.log.warn("Closing browser with errors: {}".format(e))
        self.log.info("All done")


def interactive_mode(log, shell):
    Nova.interactive_mode(shell)
    try:
        mode = InteractiveMode(log, shell)
        mode.run()
        mode.clean()
    except Exception as e:
        Nova.error(e)
