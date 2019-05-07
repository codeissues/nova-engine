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
Browser user-agent functionalities. An idea inspired by this mdn article:
https://developer.mozilla.org/en-US/docs/Web/HTTP/Browser_detection_using_the_user_agent
"""

from re import compile


ENGINES = [
    ["blink", r"Chrome/\d+", "Chrome"],
    ["gecko", r"Gecko/\d+", "Firefox"],
    ["webkit", r"AppleWebKit/\d+", "Safari"],   # not supported
    ["trident", r"Trident/\d+", "Edge"],        # not supported
    ["presto", r"Opera/\d+", "Opera"],          # not supported
]


def detect_engine(user_agent, engines=ENGINES):
    for engine, signature, browser in engines:
        regex = compile(signature)
        if len(regex.findall(user_agent)) == 0:
            continue
        return engine, browser
    raise ValueError("Cannot detect engine by given user-agent")


def detect_browser(user_agent):
    pass
