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
Update mode wrapper.
"""

from __future__ import print_function

from zipfile import ZipFile
from json import loads

from db import DB
from nova import Nova


class UpdateMode(Nova.Mode):

    VALID_FILES = ("events.json", "browsers.json", "drivers.json",
                   "system.json", "javascript.json")

    db, data, zip_ = None, None, None

    def __init__(self, log, shell):
        self.log = log
        self.log.info("Starting...")
        self.shell = shell
        self.db = DB(Nova.DATABASE)

    def read_zip(self):
        self.zip_ = ZipFile(self.shell.update_system, r"r")
        return self

    def from_json(self, data):
        return loads(self.zip_.read(data))

    def from_file(self, filename):
        return filename.replace(".json", "")

    def validate_content(self):
        return {f for f in self.zip_.namelist() if f in self.VALID_FILES}

    def prepare_data(self):
        content = self.read_zip().validate_content()
        self.data = {self.from_file(d):self.from_json(d) for d in content}
        return self

    def create_events_table(self):
        self.log.info("Checking 'events' table...")
        self.db.create_table("events", ("event TEXT PRIMARY KEY",
            "getter TEXT NOT NULL", "setter TEXT NOT NULL"))
        return self

    def create_drivers_table(self):
        self.log.info("Checking 'drivers' table...")
        self.db.create_table("drivers", ("name TEXT PRIMARY KEY",
            "browser TEXT NOT NULL", "browser_bin TEXT NOT NULL",
            "driver TEXT NOT NULL", "driver_bin TEXT NOT NULL"))
        return self

    def create_browsers_table(self):
        self.log.info("Checking 'browsers' table...")
        self.db.create_table("browsers", ("browser TEXT PRIMARY KEY",
            "args TEXT NOT NULL", "engine TEXT NOT NULL",
            "download TEXT NOT NULL"))
        return self

    def create_system_table(self):
        self.log.info("Checking 'system' table...")
        self.db.create_table("system",
            ("key TEXT PRIMARY KEY", "value TEXT NOT NULL"))
        return self

    def create_javascript_table(self):
        self.log.info("Checking 'javascript' table...")
        self.db.create_table("javascript",
            ("key TEXT PRIMARY KEY", "value TEXT NOT NULL"))
        return self

    def update_events_table(self):
        for name, data in self.data.get("events").iteritems():
            getter = data.pop("getter")
            setter = data.pop("setter")
            try:
                self.db.upsert("events", (name, getter, setter))
                self.log.info("Updating 'events' table with '{}'...".format(name))
            except Exception as e:
                self.log.info("Skiping '{}' because: {}".format(name, e))
        return self

    def update_drivers_table(self):
        for name, data in self.data.get("drivers").iteritems():
            br, br_bin = data.pop("browser")
            dv, dv_bin = data.pop("driver")
            try:
                self.db.upsert("drivers", (name, br, br_bin, dv, dv_bin))
                self.log.info("Updating 'drivers' table with '{}'...".format(name))
            except Exception as e:
                self.log.info("Skiping '{}' because: {}".format(name, e))
        return self

    def update_browsers_table(self):
        for browser, data in self.data.get("browsers").iteritems():
            args = data.pop("args")
            engine = data.pop("engine")
            download = data.pop("download")
            try:
                self.db.upsert("browsers", (browser, args, engine, download))
                self.log.info("Updating 'browsers' table with '{}'...".format(browser))
            except Exception as e:
                self.log.info("Skiping '{}' because: {}".format(browser, e))
        return self

    def update_system_table(self):
        for key, val in self.data.get("system").iteritems():
            try:
                self.db.upsert("system", (key, val))
                self.log.info("Updating 'system' table with '{}'='{}'".format(key, val))
            except Exception as e:
                self.log.info("Skiping '{}' because: {}".format(key, e))
        return self

    def update_javascript_table(self):
        for key, val in self.data.get("javascript").iteritems():
            try:
                self.db.upsert("javascript", (key, val))
                self.log.info("Updating 'javascript' table with '{}'='{}'".format(key, val))
            except Exception as e:
                self.log.info("Skiping '{}' because: {}".format(key, e))
        return self

    def run(self):
        self.db.open().cursor()
        self.db.reset()
        self.prepare_data()
        self.create_system_table().update_system_table()
        self.create_events_table().update_events_table()
        self.create_drivers_table().update_drivers_table()
        self.create_javascript_table().update_javascript_table()
        self.create_browsers_table().update_browsers_table()

    def clean(self):
        self.db.close()
        self.log.info("Successfully updated")


def update_mode(log, shell):
    Nova.update_mode(shell)
    try:
        mode = UpdateMode(log, shell)
        mode.run()
        mode.clean()
    except Exception as e:
        Nova.error(e)
