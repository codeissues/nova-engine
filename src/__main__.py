#!/usr/bin/env python
#
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

from util.log import Log
from util.shell import Shell
from util.updater import bootstrap, Updater
from util.analyze_mode import analyze_mode
from util.friend_mode import friend_mode
from util.update_mode import update_mode
from util.learn_mode import learn_mode
from util.work_mode import work_mode
from util.scan_mode import scan_mode
from util.interactive_mode import interactive_mode


if __name__ == "__main__":
    bootstrap()

    # read shell arguments
    shell, parser = Shell.read_args()

    # initialize logging system
    log = Log(level=shell.verbose, filename=shell.logfile)

    # update application resources
    if any((shell.learn,
            shell.task,
            shell.scan_system,
            shell.analyze_file,
            shell.interactive)):
        Updater.run(log)

    # update mode
    if shell.update_system:
        update_mode(log, shell)

    # launch generate mode
    elif shell.learn:
        learn_mode(log, shell)

    # launch working mode
    elif shell.task:
        work_mode(log, shell)

    # scan system
    elif shell.scan_system:
        scan_mode(log, shell)

    # analyze nvs file for current system state and database
    elif shell.analyze_file:
        analyze_mode(log, shell)

    # launch interactive mode
    elif shell.interactive:
        interactive_mode(log, shell)

    # print nova welcome message
    else:
        friend_mode() and parser.print_help()
