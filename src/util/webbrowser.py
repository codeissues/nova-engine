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
Web browser to create and reproduce sample scripts.
"""

from tools import save_html
from capabilities import Capabilities

from core.schema import Schema
from core.browser import Browser


class WebBrowser(Browser):

    JAVASCRIPT_INJECTION = r""

    @classmethod
    def set_logger(cls, logger):
        cls.log = logger

    @classmethod
    def set_script(cls, script):
        cls.JAVASCRIPT_INJECTION = script

    def inject_nova(self):
        self.run_js(self.JAVASCRIPT_INJECTION)

    def run_js(self, js):
        return self.browser.execute_script(js)

    def run_action(self, event):
        if not isinstance(event, Schema):
            raise TypeError("Event not implemented with schema")
        name = event.__class__.__name__
        return self.action(name, event._setter, event.timestamp)

    def setup(self):
        # NOTE: Apparently, none of Chrome & Firefox validate SSL for websocket
        # connections nor does it check if the SSL is signed by a CA, nor does
        # it check if the SSL for ws is the same with HTTPS...
        self.params = Capabilities.get_params(self.driver.lower())

    def on_page_load(self):
        self.inject_nova()

    def save(self):
        file_, dir_ = save_html(self.browser.page_source, self.url, root_dir=self.SAVE_PATH)
        return "{}/{}".format(dir_, file_)

    def before_action(self, name, event, timestamp):
        self.log("Running event: {}".format(name))

    def after_action(self, name, event, timestamp):
        self.log("Timelapse (s): {}".format(timestamp))
