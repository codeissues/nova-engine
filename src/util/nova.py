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
Nova application wrapper
"""

from webdriver import WebDriver
from tools import nicefy

from core.app import Application


class Nova(Application):

    DATABASE = ".db"

    browser, scan = None, None
    browser_pid, browser_path, browser_version = None, None, None
    driver_pid, driver_path, driver_version = None, None, None

    @classmethod
    def print_welcome(cls):
        credits = {
            "app": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "author": cls.AUTHOR_EMAIL,
        }
        print(" _ __   _____   ____ _ ")
        print("| '_ \ / _ \ \ / / _` |")
        print("| | | | (_) \ V / (_| |")
        print("|_| |_|\___/ \_/ \__,_|")
        print("")
        print("{app} v{version} (c) {author}".format(**credits))
        print("")
        return True

    @classmethod
    @nicefy
    def print_system(cls):
        print("\033[1mScanning system for {} browser...\033[0m".format(cls.browser))
        print("Installed browser name: {}".format(cls.browser_name))
        print("Installed browser path: {}".format(cls.browser_path))
        print("Installed browser version: {}".format(cls.browser_version))
        print("Installed driver name: {}".format(cls.driver_name))
        print("Installed driver path: {}".format(cls.driver_path))
        print("Installed driver version: {}".format(cls.driver_version))
        print("")
        browser_instances = len(cls.browser_pid)
        if browser_instances > 0:
            print("Detected {} {} instance(s) running".format(browser_instances, cls.browser_name))
        driver_instances = len(cls.driver_pid)
        if driver_instances > 0:
            print("Detected {} {} instance(s) running".format(driver_instances, cls.driver_name))
        if browser_instances > 0 or driver_instances > 0:
            try:
                answer = raw_input("Attempt to close opened instances? [y/N] ")
            except KeyboardInterrupt:
                raise SystemExit("")
            if answer == "y":
                print("Closing other instances...")
                try:
                    cls.close_instances()
                except:
                    print("Cannot close other instances. Try closing manually")
            else:
                print("Notice: multiple instances may slow down performance")
            print("")
        return True

    @classmethod
    def system_scan(cls, browser):
        cls.browser = browser
        cls.scan = WebDriver.builder(browser=browser)
        cls.browser_pid = cls.scan.get_browser_pid()
        cls.browser_path = cls.scan.get_browser_path()
        cls.browser_version = cls.scan.get_browser_version()
        cls.browser_name = cls.scan.browser_name
        cls.driver_pid = cls.scan.get_driver_pid()
        cls.driver_path = cls.scan.get_driver_path()
        cls.driver_version = cls.scan.get_driver_version()
        cls.driver_name = cls.scan.driver_name
        return True

    @classmethod
    def scan_system(cls):
        for browser in WebDriver.DRIVERS.iterkeys():
            cls.system_scan(browser)
            cls.print_system()
        print("\033[1mSystem scan completed\033[0m")

    @classmethod
    def close_instances(cls):
        pids = cls.browser_pid + cls.driver_pid
        for pid in pids:
            cls.scan.kill_process(pid)
        return True

    @classmethod
    def overview(cls, shell):
        print("Detected the following parameters...")
        for flag, value in shell.__dict__.iteritems():
            print("{}: \033[1m{}\033[0m".format(flag.rjust(15, " "), value))
        if not shell.rebuild_cache and (shell.disable_ui or shell.minify_ui):
            print("Notice: customizable flags require a one time run with -R")
        print("")
        try:
            raw_input("Press any key to continue...\n")
            print("Nova is running your script. Please stand by...\n")
        except:
            raise SystemExit

    @classmethod
    def error(cls, error):
        raise SystemExit("\033[1mSomething is wrong...\033[0m\n{}".format(error))

    @classmethod
    def learn_mode(cls, shell):
        if not shell.browser:
            raise SystemExit("Cannot launch learning mode without a browser. Try -h")
        if not shell.starturl:
            raise SystemExit("Cannot launch learning mode without an URL. Try -h")
        if not shell.silent:
            cls.print_welcome()
        cls.system_scan(browser=shell.browser)
        if not shell.silent:
            cls.print_system()
            if shell.review_shell:
                cls.overview(shell)
        return cls

    @classmethod
    def work_mode(cls, shell):
        try:
            open(shell.task).close()
        except Exception as e:
            raise SystemExit("Cannot open nvs file from {}".format(shell.task))
        if shell.browser:
            print("Notice: browser override detected")
        if shell.starturl:
            raise SystemExit("Cannot set an URL in working mode. Try -h")
        if not shell.silent:
            cls.print_welcome()
            if shell.review_shell:
                cls.overview(shell)
        return cls

    @classmethod
    def scan_mode(cls, shell):
        if not shell.silent:
            cls.print_welcome()
        cls.scan_system()
        return cls

    @classmethod
    def update_mode(cls, shell):
        if not shell.silent:
            cls.print_welcome()
        cls.update_system(shell)
        return cls

    @classmethod
    def update_system(cls, shell):
        try:
            open(shell.update_system).close()
        except Exception as e:
            raise SystemExit("Cannot open file from {}".format(shell.update_system))
        print("\033[1mNova will update on your system\033[0m")
        try:
            raw_input("Press any key to continue...\n")
        except:
            raise SystemExit

    @classmethod
    def analyze_mode(cls, shell):
        if not shell.silent:
            cls.print_welcome()
        try:
            open(shell.analyze_file).close()
        except Exception as e:
            raise SystemExit("Cannot open file from {}".format(shell.analyze_file))

    @classmethod
    def interactive_mode(cls, shell):
        if not shell.browser:
            raise SystemExit("Cannot launch interactive mode without a browser. Try -h")
        if not shell.silent:
            cls.print_welcome()
        cls.system_scan(browser=shell.browser)
        if not shell.silent:
            cls.print_system()
            if shell.review_shell:
                cls.overview(shell)
        return cls
