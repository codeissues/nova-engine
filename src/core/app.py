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
Application class object
"""

from xvfbwrapper import Xvfb


class Application(object):

    APP_NAME = "Nova"
    APP_VERSION = "0.1"

    AUTHOR_NAME = "Alexandru Catrina"
    AUTHOR_EMAIL = "alex@codeissues.net"

    class Mode(object):

        def run(self, *args, **kwargs):
            raise NotImplementedError("Method not implemented")

        def clean(self, *args, **kwargs):
            raise NotImplementedError("Method not implemented")

    class Display(object):

        PARAMS = ("width", "height", "colordepth")

        VirtualScreen = Xvfb

        class SystemScreen(object):

            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                pass

            def __exit__(self, type, value, tb):
                pass

    class Updater(object):

        def commit(self, *args, **kwargs):
            raise NotImplementedError("Method not implemented")

        def rollback(self, *args, **kwargs):
            raise NotImplementedError("Method not implemented")
