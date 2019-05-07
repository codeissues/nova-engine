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
WebDriver detector and installer
"""

from subprocess import CalledProcessError, check_output


class WebDriver(object):

    DRIVERS = {
        "firefox": {
            "browser": ("firefox", "/usr/bin/firefox"),
            "driver": ("geckodriver", "/usr/local/bin/geckodriver"),
        },
        "chrome": {
            "browser": ("google-chrome", "/opt/google/chrome/google-chrome"),
            "driver": ("chromedriver", "/usr/local/bin/chromedriver"),
        }
    }

    BROWSER, DRIVER = "browser", "driver"
    GET_PID, WHICH, VERSION_FLAG = "pidof", "which", "--version"
    KILL_PID, SIGKILL = "kill", "-9"
    NOTHING = ""

    def __init__(self, schema):
        self.schema = schema
        self.browser_name, self.browser_path = self.schema.get(self.BROWSER)
        self.driver_name, self.driver_path = self.schema.get(self.DRIVER)

    def get_browser_pid(self):
        return self.get_pid(self.browser_name)

    def get_browser_path(self):
        return self.get_path(self.browser_name).strip()

    def get_browser_version(self):
        version = self.get_version(self.browser_name)
        if not version:
            version = self.get_version(self.browser_path)
        return version.strip()

    def get_driver_pid(self):
        return self.get_pid(self.driver_name)

    def get_driver_path(self):
        return self.get_path(self.driver_name).strip()

    def get_driver_version(self):
        version = self.get_version(self.driver_name)
        if not version:
            version = self.get_version(self.driver_path)
        return version.strip()

    def get_version(self, process):
        return self.get_results([process, self.VERSION_FLAG])

    def get_path(self, process):
        return self.get_results([self.WHICH, process])

    def get_pid(self, process):
        results = self.get_results([self.GET_PID, process]).split()
        return map(int, results)

    def get_results(self, *args):
        try:
            return check_output(*args)
        except CalledProcessError:
            return self.NOTHING
        except OSError:
            return self.NOTHING

    def kill_process(self, pid):
        return self.get_results([self.KILL_PID, self.SIGKILL, str(pid)])

    @classmethod
    def builder(cls, browser=None, drivers=None):
        if browser is None:
            raise TypeError("Missing parameter: expecting browser parameter")
        if drivers is None:
            drivers = cls.DRIVERS
        schema = drivers.get(browser.lower())
        if schema is None:
            raise TypeError("Browser '{}' not installed on system".format(browser))
        return cls(schema)
