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
Execute from shell.
"""

from argparse import ArgumentParser


class Shell(object):

    __shell = {
        "description": "Nova Shell - Browser automation with virtual framebuffer support"
    }

    __opts = (
        {
            ("learn", "l"): {
                "action": "store_true",
                "help": "open an instance and generate a nvs (learning mode)"
            },
            ("task", "t"): {
                "action": "store",
                "dest": "task",
                "help": "open an instance and run task from nvs (working mode)"
            },
            ("scan-system", "s"): {
                "action": "store_true",
                "dest": "scan_system",
                "help": "scan current system for opened drivers and browsers"
            },
            ("update-system", "u"): {
                "action": "store",
                "dest": "update_system",
                "help": "update database on current system"
            },
            ("analyze-file", "a"): {
                "action": "store",
                "dest": "analyze_file",
                "help": "test nvs file against current system setup and database"
            },
            ("interactive", "i"): {
                "action": "store_true",
                "dest": "interactive",
                "help": "run an interactive session"
            },
        }
    )

    __args = {
        ("browser", None): {
            "action": "store",
            "dest": "browser",
            "help": "use choosen browser (if available)"
        },
        ("resolution", None): {
            "action": "store",
            "dest": "resolution",
            "help": "use choosen resolution WxH in pixels"
        },
        ("starturl", None): {
            "action": "store",
            "dest": "starturl",
            "help": "set a starting url to open"
        },
        ("headless", None): {
            "action": "store_true",
            "help": "run browser headless"
        },
        ("verbose", "v"): {
            "action": "count",
            "dest": "verbose",
            "default": 0,
            "help": "set output verbosity"
        },
        ("session", None): {
            "action": "store",
            "dest": "session",
            "help": "set sessions path"
        },
        ("silent", "S"): {
            "action": "store_true",
            "help": "no output (errors are still printed)"
        },
        ("rebuild-cache", "R"): {
            "action": "store_true",
            "dest": "rebuild_cache",
            "help": "rebuild cached injection script"
        },
        ("disable-ui", None): {
            "action": "store_true",
            "dest": "disable_ui",
            "help": "disable ui animations on injection script"
        },
        ("minify-ui", None): {
            "action": "store_true",
            "dest": "minify_ui",
            "help": "minify generated injection script"
        },
        ("review-shell", None): {
            "action": "store_true",
            "dest": "review_shell",
            "help": "print a list of all detected parameters"
        },
        ("fps", None): {
            "action": "store",
            "default": 1,
            "help": "change recorder FPS"
        },
        ("record", None): {
            "action": "store",
            "help": "set recorded output path and video format"
        },
        ("merge-session", None): {
            "action": "store_true",
            "dest": "merge_session",
            "help": "merge nvs files into one final nvs file"
        },
        ("logfile", None): {
            "action": "store",
            "dest": "logfile",
            "help": "log std* to file"
        }
    }

    def __init__(self):
        self.parser = ArgumentParser(**self.__shell)
        grouped = self.parser.add_mutually_exclusive_group()
        for flags, opts in self.__opts.iteritems():
            self.add(grouped, flags, opts)
        for flags, opts in self.__args.iteritems():
            self.add(self.parser, flags, opts)
        self.args = self.parser.parse_args()

    def add(self, parser, flags, opts):
        name, short = flags
        if short is None:
            parser.add_argument(r"--{}".format(name), **opts)
        else:
            parser.add_argument(r"-{}".format(short), r"--{}".format(name), **opts)

    @classmethod
    def read_args(cls):
        shell = cls()
        return shell.args, shell.parser
