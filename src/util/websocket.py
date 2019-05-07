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
Local server to create and reproduce sample scripts.
"""

from tools import parse_url, create_nvs_file, update_nvs_session

from core.server import Server


class WebSocket(Server.WebSocketServer):

    SCRIPTS_PATH = r"dump"

    connect_hooks, disconnect_hooks = [], []
    session, paths = None, None

    @classmethod
    def set_scripts_path(cls, path):
        if isinstance(path, (str, unicode)) and len(path) > 0:
            cls.SCRIPTS_PATH = path

    @classmethod
    def set_ssl_path(cls, certfile, keyfile):
        if isinstance(certfile, (str, unicode)) and len(certfile) > 0:
            cls.SSL.update({"certfile": certfile})
        if isinstance(keyfile, (str, unicode)) and len(keyfile) > 0:
            cls.SSL.update({"keyfile": keyfile})

    @classmethod
    def add_connection_hook(cls, func):
        cls.connect_hooks.append(func)

    @classmethod
    def add_disconnection_hook(cls, func):
        cls.disconnect_hooks.append(func)

    def loop_hooks(self, hooks):
        return all([f(self) for f in hooks])

    def check_origin(self, host):
        self.paths = parse_url(host)
        return True

    def on_connect_callback(self):
        self.session = create_nvs_file(*self.paths, root_dir=self.SCRIPTS_PATH)
        self.loop_hooks(self.connect_hooks)

    def on_disconnect_callback(self):
        self.session, self.paths = None, None
        self.loop_hooks(self.disconnect_hooks)

    def on_message_callback(self):
        update_nvs_session(self.message, *self.session)
