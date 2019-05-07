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
JavaScript events list:
    - getter used to obtain data
    - setter used to reproduce data
"""

class Events(object):

    EVENTS = {
        "click": {
            "getter": r"function(m){var s=function(n){var y=n.localName;y+=n.id!=''?'#'+n.id:'';y+=n.className!=''?'.'+n.className.replace(/\s/g,'.'):'';return y;};return s(m.parentElement)+' '+s(m);}(e.target)",
            "setter": r"(function(d,i,z,b){var n=d.getElementById(i),e;if(n){n.style.display=z;e=d.elementFromPoint($clientX,$clientY);n.style.display=b;}if(!e)e=d.querySelector('$data');if(e)e.click();}(document,'mouse__pointer','none','block'))"
        },
        "mousemove": {
            "getter": r"null",
            "setter": r"(function(d,e,i){var x=$clientX,y=$clientY,n=d.getElementById(i);if(n==null){n=d.createElement(e);d.body.appendChild(n);n.id=i;n.style.position='fixed';n.style.width='16px';n.style.height='16px';n.style.marginTop='-8px';n.style.marginLeft='-8px';n.style.background='#fff';n.style.borderRadius='50px';n.style.border='3px solid #384c8c';n.style.zIndex=999999999;}n.style.top=y+'px';n.style.left=x+'px';dispatchEvent(new MouseEvent('mousemove',{clientX:x,clientY:y}));}(document,'div','mouse__pointer'))"
        },
        "scroll": {
            "getter": r"window.scrollY",
            "setter": r"window.scrollTo(0, $data)"
        }
    }

    @classmethod
    def builder(cls, schema, events=None):
        if events is None:
            events = cls.EVENTS
        for name, methods in events.iteritems():
            clazz = "{}Event".format(name.capitalize())
            event = type(clazz, (schema, object), {
                "_getter": methods.get("getter"),
                "_setter": methods.get("setter"),
                "_name": name
            })
            yield name, event
