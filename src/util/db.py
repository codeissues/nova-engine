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
SQLite wrapper.

Sample event:

    "scroll": {
        "getter": r"window.scrollY",
        "setter": r"window.scrollTo(0, $data)"
    }

Sample driver:

    "firefox": {
        "browser": ("firefox", "/usr/bin/firefox"),
        "driver": ("geckodriver", "/usr/local/bin/geckodriver"),
    }

"""

from sqlite3 import connect


class DB(object):

    database, db, _ = None, None, None

    def __init__(self, database):
        self.database = database

    def open(self):
        self.db = connect(self.database)
        return self

    def close(self):
        self.db.close()
        return self

    def cursor(self):
        self._ = self.db.cursor()
        return self._

    def query(self, sql, *args):
        if self._ is None:
            self.cursor()
        self._.execute(sql, *args)
        self.commit()
        return self

    def commit(self):
        self.db.commit()
        return self

    def reset(self):
        self.query("SELECT name, type FROM sqlite_master WHERE type IS 'table'")
        sql = "DROP TABLE IF EXISTS {table}"
        for table_name, _ in self._.fetchall():
            self.query(sql.format(table=table_name))
        return self

    def create_table(self, table_name, table_fields):
        sql = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
        query = sql.format(table=table_name, fields=",".join(table_fields))
        self.query(query)
        return self

    def upsert(self, table_name, row_values):
        sql = "INSERT OR REPLACE INTO {table} VALUES ({values})"
        values = ["?" for _ in row_values]
        query = sql.format(table=table_name, values=",".join(values))
        self.query(query, row_values)
        return self._.lastrowid

    def select(self, table_name, *fields):
        sql = "SELECT {fields} FROM {table}"
        query = sql.format(table=table_name, fields=",".join(fields))
        self.query(query)
        return self._.fetchall()

    def filter(self, table_name, where, *fields):
        sql = "SELECT {fields} FROM {table} WHERE {where}"
        query = sql.format(table=table_name, where=where, fields=",".join(fields))
        self.query(query)
        return self._.fetchall()


class Schema(DB):

    def load_events(self):
        self.open().cursor()
        gt, st = "getter", "setter"
        fields = ["event", "getter", "setter"]
        rows = self.select("events", *fields)
        self.close()
        return {e:{gt:g, st:s} for e, g, s in rows}

    def load_drivers(self):
        self.open().cursor()
        bk, dk = "browser", "driver"
        fields = ["name", "browser", "browser_bin", "driver", "driver_bin"]
        rows = self.select("drivers", *fields)
        self.close()
        return {e:{bk:(b,bb), dk:(d,db)} for e, b, bb, d, db in rows}

    def load_system_ssl(self):
        self.open().cursor()
        rows = self.filter("system", r"key like 'ssl_%'", "key", "value")
        self.close()
        return {k.replace("ssl_", ""):v for k, v in rows}

    def load_startup_javascript(self):
        self.open().cursor()
        rows = self.filter("javascript", r"key='startup'", "key", "value")
        self.close()
        results = {k:v for k, v in rows}
        return results.get("startup", "")

    def load_browsers(self):
        self.open().cursor()
        rows = self.select("browsers", "browser", "args")
        self.close()
        return {br:args for br, args in rows}
