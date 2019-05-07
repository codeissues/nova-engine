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
JavaScript scripts and helper methods to generate sample Nova scripts.
"""

from time import time
from re import sub
from os import path, makedirs


HEAD = r"""ws.onopen = function(){{
ws.send(w.location.href);
ws.send(new Date().getTime());
ws.send(w.navigator.userAgent);
ws.send([w.innerWidth,w.innerHeight,s.width,s.height,s.colorDepth,s.pixelDepth,s.orientation.type.match(/landscape/)!==null?1:2].join(c));
{hook}
}};"""

TAIL = r"""ws.onclose = function(){{{hook}}};
ws.onerror = function(e){{alert(e);}};"""

NOTIFICATION = """!(function(color, textContent, ttl){{
var notification = document.createElement('div');
var doc = document.querySelector('body');
doc.appendChild(notification);
notification.style.background = '#FFF';
notification.style.color = color;
notification.style.position = 'fixed';
notification.style.top = '0';
notification.style.left = '0';
notification.style.right = '0';
notification.style.bottom = '0';
notification.style.textAlign = 'center';
notification.style.zIndex = '999999999';
notification.style.fontSize = '32px';
notification.style.fontFamily = 'monospace';
notification.style.paddingTop = (window.innerHeight+32)/2+'px';
notification.style.opacity = 0;
notification.textContent = textContent;
notification.id = 'nova__notification';
var i=0,loop = setInterval(function(n){{
n.style.opacity=i*0.1;i++;
}},ttl/10,notification);
setTimeout(function(n){{
clearInterval(loop);
loop=setInterval(function(){{n.style.opacity=i*0.1;i--;}},ttl/10);
setTimeout(function(){{clearInterval(loop);n.remove();}},ttl);
}},ttl,notification);
}}('{color}','Nova is {status}',{ttl}));"""

INJECT_CONNECTION = r"""var script = document.createElement('script');
script.type = 'text/javascript';
script.id = 'nova{uuid}';
script.innerHTML = `!(function(ws,w,s,c){{
{library}{script}
}}(new WebSocket('wss://localhost:8436'),window,screen,','));`;
var doc = document.querySelector('head');
doc.appendChild(script);"""

EVENT = r"""window.on{name}=function(e){{
var collector=['{name}'];{builder}
collector.push({getter});
ws.send(collector.join(','));
}};"""


class JS(object):

    CACHE_PATH, FILENAME = r"/tmp/nova", r"nova.inject.js"

    CONTENT, NO_NOTIFICATION = "", ""
    ON_STARTUP = ""
    HEAD, TAIL = HEAD, TAIL
    NOTIFICATION = NOTIFICATION
    INJECT_CONNECTION = INJECT_CONNECTION
    EVENT = EVENT

    @classmethod
    def notification(cls, disable_ui=False, online=True, ttl=250):
        if disable_ui:
            return cls.NO_NOTIFICATION
        color = "#79b71b";
        status = "online"
        if not online:
            color = "#e42c2c"
            status = "offline"
        return cls.NOTIFICATION.format(color=color, status=status, ttl=ttl)

    @classmethod
    def read_script(cls, read_cached=True, minify=True, disable_ui=False):
        if not path.exists(cls.CACHE_PATH):
            makedirs(cls.CACHE_PATH)
        filename = r"{}/{}".format(cls.CACHE_PATH, cls.FILENAME)
        try:
            if not read_cached:
                raise ValueError(r"Force to except...")
            with open(filename, "rb") as cache:
                cls.script = cache.read()
            return True
        except:
            cls.generate_script(minify, disable_ui)
            with open(filename, "wb") as cache:
                cache.write(cls.script)
            return False

    @classmethod
    def generate_script(cls, minify=False, disable_ui=False):
        head = cls.HEAD.format(hook=cls.notification(disable_ui, True))
        tail = cls.TAIL.format(hook=cls.notification(disable_ui, False))
        script = r"".join([head, cls.CONTENT, tail])
        timestamp = int(time())
        if not isinstance(cls.ON_STARTUP, (str, unicode)):
            cls.ON_STARTUP = ""
        options = {
            "script": script,
            "library": cls.ON_STARTUP,
            "uuid": timestamp
        }
        cls.script = cls.INJECT_CONNECTION.format(**options)
        if minify:
            cls.script = cls.script.replace("\n", "")
            cls.script = sub(r"\s{2,}", " ", cls.script)
            cls.script = cls.script.replace(" = ", "=").replace("; ", ";")
        return cls

    @classmethod
    def add_events(cls, events):
        for k, e in events.iteritems():
            cls.CONTENT += cls.EVENT.format(name=k, \
                builder=e.builder(), getter=e.getter())
        return cls
