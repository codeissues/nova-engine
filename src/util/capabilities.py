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
Browser capabilities
"""


class Capabilities(object):

    BROWSERS = {}
    BROWSER_ARGS = {
        "chrome": "chrome_options",
        "firefox": "firefox_options",
        "opera": "opera_options"
    }
    MODULE = "selenium.webdriver.{}.options"

    @classmethod
    def get_args(cls, browser):
        if not isinstance(browser, (str, unicode)):
            raise TypeError("Unexpected type of input 'browser'")
        values = []
        args = cls.BROWSERS.get(browser)
        if args is not None:
            values = [x for x in args.split(" ") if len(x) > 0]
        return values

    @classmethod
    def get_params(cls, browser):
        args = cls.get_args(browser)
        if len(args) == 0:
            return
        browser_args = cls.BROWSER_ARGS.get(browser)
        if browser_args is None:
            return
        opts = cls.get_options(browser)
        [opts.add_argument(o) for o in args if o]
        return {browser_args: opts}

    @classmethod
    def get_options(cls, browser):
        module = cls.MODULE.format(browser)
        options = __import__(module, globals(), locals(), "Options", -1)
        return options.Options()
