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
Analyze mode wrapper.
"""

from tools import get_db_meta, check_url, timestamp_date
from nova import Nova
from reader import Reader
from webdriver import WebDriver
from webbrowser import WebBrowser
from user_agent import detect_engine

from core.events import Events
from core.schema import Schema
from core.javascript import JS


class AnalyzeMode(Nova.Mode):

    nvs, events, drivers = None, None, None

    def __init__(self, log, filepath):
        self.info = lambda s: log.info("\033[0;32m{}\033[0m".format(s))
        self.warn = lambda s: log.warn("\033[0;31m{}\033[0m".format(s))
        self.filepath = filepath
        self.db = get_db_meta()

    def test_db(self):
        if self.db.missing:
            return self.warn("Nova database is not in system PATH!")
        self.info("Nova database found on system!")
        self.info("Path \t{}".format(self.db.file))
        self.info("Created on \t{}".format(self.db.created_date))
        self.info("Modified on \t{}".format(self.db.modified_date))
        self.info("Be sure to keep Nova up-to-date [nova -u pkg]")

    def test_file(self):
        self.nvs = Reader(self.filepath)
        if self.nvs is None:
            self.warn("Invalid or corrupted nvs file! Nothing to do now...")
            raise SystemExit
        self.info("Loading scenario from nvs file: {}".format(self.filepath))
        return self

    def test_url(self):
        url = self.nvs.read()
        self.info("Checking URL...")
        reply = check_url(url)
        if reply is None:
            self.info("URL is OK")
        else:
            self.warn("URL is not alright: {}".format(reply))

    def test_datetime(self):
        self.info("Converting timestamp...")
        try:
            dt = timestamp_date(self.nvs.read())
            self.info("Scenario created on {}".format(dt))
        except Exception as e:
            self.warn("Cannot understand timestamp... {}".format(e))

    def test_browser(self):
        ua_string = self.nvs.read()
        self.info("Checking browser...")
        try:
            engine, browser = detect_engine(ua_string)
            driver = WebDriver.builder(browser)
            self.info("Current system supports scenario browser!")
            self.info("Browser name \t{}".format(driver.browser_name))
            self.info("Browser path \t{}".format(driver.browser_path))
            self.info("WebDriver name \t{}".format(driver.driver_name))
            self.info("WebDriver path \t{}".format(driver.driver_path))
        except Exception as e:
            self.warn("Notice: {}".format(e))
            self.warn("System does not support scenario browser!")
            self.warn("You can force task to use another browser with the same engine")
            self.warn("E.g. nova -vt task --headless --browser different_browser")

    def test_resolution(self):
        display = self.nvs.read()
        self.info("Checking display resolution...")
        try:
            bw, bh, dw, dh, cd, _, _ = display.split(",")
            self.info("Browser resolution \t{}x{}".format(bw, bh))
            self.info("Display resolution \t{}x{}x{}".format(dw, dh, cd))
            if int(bw) > WebBrowser.MAX_WIDTH:
                self.warn("Browser width exceeds MAX_WIDTH constant")
            if int(bh) > WebBrowser.MAX_HEIGHT:
                self.warn("Browser height exceeds MAX_HEIGHT constant")
        except Exception as e:
            self.warn("Cannot determine display resolution: {}".format(e))

    def test_events(self):
        events = {}
        self.info("Checking events...")
        max_split = len(Schema.ATTRIBUTES) + 1
        while not self.nvs.ended():
            action = self.nvs.read()
            if action is None:
                continue
            event, _, _, _, _, _, _, _, _, _ = action.split(",", max_split)
            if events.has_key(event):
                events[event] += 1
            else:
                events.update({event: 1})
        missing_events = 0
        if not events:
            self.warn("No events in scenario. Something is very wrong!")
        else:
            self.info("Found the following events in scenario...")
            self.info("Event name   | Stats | Installed")
            for e, t in events.iteritems():
                if Events.EVENTS.has_key(e):
                    installed = "YES"
                else:
                    installed = "n/a"
                    missing_events += 1
                self.info("{} \t| {} \t| {}".format(e, t, installed))
        if missing_events > 0:
            self.warn("Scenario has {} unhandled events. This may compromise final output".format(missing_events))
            self.warn("Review the list above for missing events from current database")
        else:
            self.info("Database is up-to-date with scenario context!")

    def test_javascript(self):
        pass

    def run(self):
        self.test_db()
        self.test_file()
        self.test_url()
        self.test_datetime()
        self.test_browser()
        self.test_resolution()
        self.test_events()
        self.test_javascript()
        return self

    def clean(self):
        return self


def analyze_mode(log, shell):
    Nova.analyze_mode(shell)
    try:
        mode = AnalyzeMode(log, shell.analyze_file)
        mode.run().clean()
    except Exception as e:
        Nova.error(e)
