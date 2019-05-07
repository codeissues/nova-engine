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
Create a browser instance to execute script commands.
"""

from __future__ import print_function

from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, WebDriverException


class Browser(object):

    MAX_WAIT_TIME = 1
    SAVE_PATH = r"/tmp/nova/saved"
    MAX_WIDTH = 8192
    MAX_HEIGHT = 4320

    log = lambda self, message: print(message)
    calltime = 0
    loaded, closed = False, False
    url, browser, width, height, params = None, None, 0, 0, None
    driver = None

    def __init__(self, browser, width=0, height=0):
        self.init_resolution(width, height)
        self.init_browser(browser)
        self.log("Browser initialized")

    def init_resolution(self, width, height):
        if not isinstance(width, int):
            width = int(width)
        if not isinstance(height, int):
            height = int(height)
        if not 1 < width < self.MAX_WIDTH or not 1 < height < self.MAX_HEIGHT:
            raise ValueError("Unsupporter format: {}x{}".format(width, height))
        self.width = width
        self.height = height

    def init_browser(self, browser):
        if not isinstance(browser, (str, unicode)):
            raise ValueError(u"Unexpected {} datatype".format(type(browser)))
        self.driver = browser.capitalize()
        if not hasattr(webdriver, self.driver):
            raise ValueError(u"Unsupported browser: '{}'".format(self.driver))
        self.log(u"Opening {} browser...".format(self.driver))
        self.setup()
        if not isinstance(self.params, dict):
            self.params = {}
        for k in self.params.iterkeys():
            self.log(u"Loading param '{}'".format(k))
        self.browser = getattr(webdriver, self.driver)(**self.params)
        self.browser.implicitly_wait(self.MAX_WAIT_TIME)
        self.browser.set_window_position(0, 0)
        try:
            self.set_viewport_size(self.width, self.height)
        except:
            self.browser.set_window_size(self.width, self.height)

    def set_viewport_size(self, width, height):
        size = self.browser.execute_script("""return [
                window.outerWidth-window.innerWidth+arguments[0],
                window.outerHeight-window.innerHeight+arguments[1]
            ];""", width, height)
        self.log(u"Setting resolution to: {}x{}".format(*size))
        self.browser.set_window_size(*size)
        return self

    def open_page(self, url):
        if not isinstance(url, (str, unicode)):
            raise ValueError("Unexpected parameter type: invalid URL")
        self.url = url
        self.browser.get(url)
        self.on_page_load()
        self.loaded = True
        return self

    def close_browser(self):
        try:
            self.browser.quit()
        except Exception as e:
            self.log(u"Error: {}".format(e))
        self.closed = True
        return self

    def action(self, name, event, timestamp):
        timestamp = timestamp / 1000.
        if timestamp > 0:
            wait_time = timestamp - self.calltime
            sleep(wait_time) if wait_time > 0 else None
        else:
            timestamp = 0
        self.before_action(name, event, timestamp)
        action = self.browser.execute_script(event)
        self.after_action(name, event, timestamp)
        self.calltime = timestamp
        return action

    def before_action(self, *args):
        pass

    def after_action(self, *args):
        pass

    def setup(self, *args, **kwargs):
        pass

    def on_page_load(self, *args, **kwargs):
        pass

    def ready(self):
        return self.loaded

    def save(self):
        pass

    def ping(self):
        try:
            return self.browser.current_url
        except NoSuchWindowException:
            return None
        except WebDriverException:
            self.close_browser()
        except Exception as e:
            self.log("Error: {}".format(e))
        return None
