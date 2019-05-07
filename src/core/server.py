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
Local server serving resources to create and reproduce sample scripts.
"""

from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop


class Server(object):

    PORT = 8436

    class WebSocketServer(WebSocketHandler):

        SSL = dict(certfile="cert.pem", keyfile="key.pem")

        message = None

        @classmethod
        def run(cls, secure=True):
            app = Application([(r"/", cls)])
            server = HTTPServer(app, ssl_options=cls.SSL) if secure else app
            server.listen(Server.PORT)
            IOLoop.instance().start()

        @classmethod
        def stop(cls):
            ioloop = IOLoop.instance()
            ioloop.add_callback(ioloop.stop)

        def open(self):
            self.message = "n/a"
            self.on_connect_callback()

        def on_message(self, message):
            self.message = message
            self.on_message_callback()

        def on_close(self):
            self.message = None
            self.on_disconnect_callback()

        def check_origin(self, host):
            return True

        def on_connect_callback(self, *args, **kwargs):
            pass

        def on_disconnect_callback(self, *args, **kwargs):
            pass

        def on_message_callback(self, *args, **kwargs):
            pass
