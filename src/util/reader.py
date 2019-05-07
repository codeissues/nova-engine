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
Script reader line by line until EOF.
"""

class Reader(object):

    data, sep, script, EOF = None, "\n", None, False

    def __init__(self, filename):
        try:
            with open(filename) as script:
                self.data = script.read().strip().split(self.sep)
        except Exception as e:
            raise ValueError("Unexpected error while reading script: {}".format(e))
        self.script = self.create_script()

    def create_script(self, inverse=False):
        if not isinstance(self.data, list):
            raise ValueError("Unexpected data type: script must be a list")
        for line in self.data[-1::-1] if inverse else self.data:
            yield line

    def read(self):
        try:
            return next(self.script)
        except StopIteration:
            self.EOF = True
            return None
        except ValueError as Error:
            raise Error
        except:
            return None

    def ended(self):
        return self.EOF
