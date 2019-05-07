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
Learning mode wrapper.
"""

from __future__ import print_function

from time import sleep

from nova import Nova
from tools import nicefy, path_exists, merge_session, track_session, lock_session
from consts import RECONNECT, CONNECTED, NO_ERROR_EXIT
from websocket import WebSocket
from webbrowser import WebBrowser

from core.worker import Worker
from core.schema import Schema
from core.events import Events
from core.javascript import JS

from libs.openssl import openssl


class LearnMode(Nova.Mode):

    RESOLUTION_PARAMS = 2
    server, browser, monitor, ping = None, None, None, None

    def __init__(self, log, shell):
        self.log = log
        self.log.info("Launching Nova in learning mode...")
        self.shell = shell
        self.secure_ws = False
        self.prepare_browser().prepare_javascript().prepare_server()

    def prepare_browser(self):
        try:
            self.browser_name = self.shell.browser
            self.browser_url = self.shell.starturl
            resolution = self.shell.resolution.split(r"x")
            if len(resolution) != self.RESOLUTION_PARAMS:
                raise TypeError(r"Invalid resolution parameters")
            self.browser_width, self.browser_height = map(int, resolution)
        except Exception as e:
            raise TypeError(r"Missing resolution parameters. See -h")
        return self

    def prepare_javascript(self):
        options = {
            "read_cached": not self.shell.rebuild_cache,
            "disable_ui": self.shell.disable_ui,
            "minify": self.shell.minify_ui
        }
        if JS.read_script(**options):
            self.log.info("Reading scripts from cache...")
        else:
            options.update({"read_cached": False})
            JS.add_events({k:v for k, v in Events.builder(Schema)})
            JS.read_script(**options)
            self.log.info("Reading generated scripts. Caching now...")
        return self

    def prepare_server(self):
        WebSocket.set_scripts_path(path=self.shell.session)
        certfile = WebSocket.SSL.get("certfile")
        keyfile = WebSocket.SSL.get("keyfile")
        if path_exists(certfile) and path_exists(keyfile):
            self.secure_ws = True
            self.log.info("Loading SSL certificates...")
        else:
            self.log.info("No SSL certificates on system. Generating...")
            if openssl(certfile, keyfile) == NO_ERROR_EXIT:
                WebSocket.set_ssl_path(certfile=certfile, keyfile=keyfile)
                self.secure_ws = True
                self.log.info("Generated SSL certificates. Using secure connection")
            else:
                self.log.warn("Failed to generate SSL certificates. Using insecure connection")
        return self

    def start_server(self, **kwargs):
        @nicefy
        def _server():
            WebSocket.add_connection_hook(lambda *_: Worker.catch(CONNECTED))
            WebSocket.add_disconnection_hook(lambda *_: Worker.catch(RECONNECT))
            WebSocket.run(secure=self.secure_ws)
        self.server = Worker(_server)
        self.server.start()
        return self

    def start_browser(self, **kwargs):
        WebBrowser.set_logger(self.log.info)
        WebBrowser.set_script(JS.script)
        self.browser = WebBrowser(self.browser_name, self.browser_width, self.browser_height)
        self.browser.open_page(self.browser_url)
        saved_page = self.browser.save()
        if saved_page is not None:
            self.log.info(u"Downloaded page at {}".format(saved_page))
        return self

    def ping_browser(self):
        return self.browser.ping() is not None

    def check_browser(self):
        if self.browser.ready() and not self.ping_browser():
            self.log.warn("Browser has been closed. Sending signal to close...")
            self.server.stop()
            return False
        return True

    def start_ping(self, **kwargs):
        @nicefy
        def _ping():
            while self.check_browser():
                sleep(1)
        self.ping = Worker(_ping)
        self.ping.start()
        return self

    def start_monitor(self, **kwargs):
        @nicefy
        def _monitor():
            while True:
                data = Worker.listen()
                if not self.ping_browser():
                    break
                elif data == RECONNECT:
                    self.log.warn("Nova is offline. Reconnecting...")
                    try:
                        self.browser.inject_nova()
                    except:
                        Worker.catch(RECONNECT)
                elif data == CONNECTED:
                    self.log.info("Nova is online!")
                else:
                    self.log.warn("Unexpected event: data={}".format(data))
        self.monitor = Worker(_monitor)
        self.monitor.start()
        return self

    def run(self):
        try:
            self.start_server().start_browser().start_monitor().start_ping()
            self.log.info("Hit ^C to exit...")
            self.close_workers()
        except KeyboardInterrupt:
            print("") # new line
            self.log.info("Safely exiting...")
        except Exception as e:
            self.log.warn("Error: %s", str(e).strip())
            self.log.warn("Nova has crashed! Hit ^C to print traceback and exit")

    def close_workers(self):
        Worker.close()
        self.monitor.join()
        self.server.join()
        self.ping.join()
        self.log.info("Closing workers...")

    def clean(self, callback=None, args=()):
        if callable(callback) and isinstance(args, tuple):
            try:
                reply = callback(*args)
                if reply is None:
                    reply = "n/a"
                self.log.info("Callback response: {}".format(reply))
            except Exception as error:
                self.log.warn("Callback error: {}".format(error))
        self.log.info("Cleaning up...")


def learn_mode(log, shell):
    Nova.learn_mode(shell)
    try:
        opts = {}
        mode = LearnMode(log, shell)
        if shell.merge_session:
            lock = lock_session()
            WebSocket.add_connection_hook(lambda this: \
                track_session(this.session, lock))
            opts.update({
                "callback": merge_session,
                "args": (lock,)
            })
        mode.run()
        mode.clean(**opts)
    except Exception as e:
        Nova.error(e)
