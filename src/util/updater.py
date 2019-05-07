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
Application resources updater and bootstrap.

Directory structure sample:

|-- .nova (resources folder)
|   |-- ssl (SSL certificates)
|   |   |-- key.pem
|   |   |-- cert.pem
|   |-- updates (database updates)
|   |   |-- update180817.zip
|   |   |-- update190817.zip
|   |   |-- ...
|   |-- .db (database)
|-- nova (binary executable)
"""

from __future__ import print_function

from tools import get_db_dir, get_db_meta
from nova import Nova
from db import Schema
from webdriver import WebDriver
from websocket import WebSocket
from capabilities import Capabilities

from core.events import Events
from core.javascript import JS


class Updater(Nova.Updater):

    dbfile = None
    log = print

    def __init__(self, db):
        self.events = Events.EVENTS
        self.drivers = WebDriver.DRIVERS
        self.ssl = WebSocket.SSL
        self.js_script = JS.ON_STARTUP
        self.capabilities = Capabilities.BROWSERS
        self.db = Schema(db)

    def commit(self):
        Events.EVENTS = self.db.load_events()
        WebDriver.DRIVERS = self.db.load_drivers()
        WebSocket.SSL = self.db.load_system_ssl()
        JS.ON_STARTUP = self.db.load_startup_javascript()
        Capabilities.BROWSERS = self.db.load_browsers()

    def rollback(self):
        Events.EVENTS = self.events
        WebDriver.DRIVERS = self.drivers
        WebSocket.SSL = self.ssl
        JS.ON_STARTUP = self.js_script
        Capabilities.BROWSERS = self.capabilities

    @classmethod
    def check(cls):
        db = get_db_meta(cls.dbfile)
        if db.missing:
            return False
        try:
            cls.log("Detected nova database file on system...")
            cls.log("Path to DB file {}".format(db.file))
            cls.log("Created on {}".format(db.created_date))
            cls.log("Last modified on {}".format(db.modified_date))
        except Exception as e:
            return False
        return True

    @classmethod
    def update(cls):
        run = cls(cls.dbfile)
        try:
            run.commit()
            run.log("Resources updated successfully...")
        except Exception as e:
            run.rollback()
            run.log("Error: {}".format(e))
            run.log("Failed to update resources. Rollbacking now...")
        return cls

    @classmethod
    def review(cls):
        for v in WebSocket.SSL.itervalues():
            cls.log("Imported SSL from '{}'...".format(v))
        for k in Events.EVENTS.iterkeys():
            cls.log("Imported javascript event '{}'...".format(k))
        for k in WebDriver.DRIVERS.iterkeys():
            cls.log("Imported driver for '{}'...".format(k))

    @classmethod
    def run(cls, log):
        cls.log = log.info
        cls.dbfile = Nova.DATABASE
        if cls.check():
            cls.update().review()
            cls.log("Booting Nova...")
        return cls


def bootstrap():
    nova_db = get_db_dir()
    if nova_db is not None:
        Nova.DATABASE = nova_db
