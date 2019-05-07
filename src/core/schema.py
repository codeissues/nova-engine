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
Javascript schema:
    _name       - event name
    timeStamp   - timestamp of event (sec)
    buttons     - mouse button or equivalent
    clientX     - cursor X position or equivalent
    clientY     - cursor Y position or equivalent
    altKey      - is true if alt key is pressed during event
    ctrlKey     - is true if ctrl key is pressed during event
    shiftKey    - is true if shift key is pressed during event
    metaKey     - is true if meta key is pressed during event (winkey or cmd)
    getter      - callback to obtain data
    setter      - callback to reproduce data
    data        - event result from getter

Sample:
    click 1289 1 5 5 0 0 0 0 h1#logo

Resources:
    https://www.w3.org/TR/DOM-Level-3-Events/#trusted-events
    https://developer.mozilla.org/en-US/docs/Web/API/Event
"""

from string import Template


class Schema(object):

    ATTRIBUTES = (
        # event key     in      out
        (r"timeStamp",  int,    int),
        (r"buttons",    int,    int),
        (r"clientX",    int,    int),
        (r"clientY",    int,    int),
        (r"altKey",     bool,   int),
        (r"ctrlKey",    bool,   int),
        (r"shiftKey",   bool,   int),
        (r"metaKey",    bool,   int),
    )

    _name, _getter, _setter = None, None, None

    timestamp, data = None, None
    buttons, x_axe, y_axe = None, None, None
    alt_key, ctrl_key, shift_key, meta_key = None, None, None, None

    separator = ","

    def __init__(self, event):
        if not isinstance(event, dict):
            raise TypeError("Unexpected event type: must be dictionary")
        if "event" in event:
            raise ValueError("Unprocessed event detected: cannot initialize")
        self.unpack_event(**event).append_xetters(event)

    def unpack_event(self, timeStamp, buttons, clientX, clientY,
                    altKey, ctrlKey, shiftKey, metaKey, data):
        self.timestamp = timeStamp
        self.buttons = buttons
        self.x_axe, self.y_axe = clientX, clientY
        self.alt_key, self.ctrl_key = altKey, ctrlKey
        self.shift_key, self.meta_key = shiftKey, metaKey
        self.data = data
        return self

    def append_xetters(self, event):
        self._getter = Template(self._getter).safe_substitute(event)
        self._setter = Template(self._setter).safe_substitute(event)

    @classmethod
    def getter(cls):
        return cls._getter

    @classmethod
    def setter(cls):
        return cls._setter

    @classmethod
    def builder(cls):
        build = r"(function(e,z,y){var v;"
        for n, t, _ in cls.ATTRIBUTES:
            build += r"v=z;if('{}' in e)".format(n)
            if t is bool:
                build += r"v=e.{}?1:0;".format(n)
            elif t is float:
                build += r"v=parseFloat(e.{}).toFixed(3);".format(n)
            elif t is int:
                build += r"v=parseInt(e.{});".format(n)
            elif t is str or t is unicode:
                build += r"v=e.{}.toString();".format(n)
            else:
                build += r"v=e.{};".format(n)
            build += r"y.push(v);"
        build += r"}(e,'',collector));"
        return build

    @classmethod
    def developer(cls, action):
        attrs_len = len(cls.ATTRIBUTES)
        attributes = action.split(cls.separator, attrs_len + 1)
        if len(attributes) == 0 or len(attributes) == attrs_len:
            raise TypeError("Unexpected length action line")
        line = zip(cls.ATTRIBUTES, attributes[1:attrs_len + 1])
        data = attributes[-1]
        schema = dict(event=attributes[0], data=data)
        for attr, value in line:
            key, type_, transform = attr
            try:
                val = type_(transform(value))
            except Exception as e:
                val = None
            schema.update({key: val})
        return schema
