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
Logging wrapper
"""

import logging


class Log(object):

    options = {
        "format": u"%(levelname)8s %(asctime)s - %(message)s"
    }

    def __init__(self, level=None, filename=None):
        if filename is not None:
            self.options.update({"filename": filename})
        if level == 1:
            level = logging.INFO
        elif level >= 2:
            level = logging.DEBUG
        else:
            level = logging.WARNING
        self.options.update({"level": level})
        logging.basicConfig(**self.options)

    def info(self, *args):
        logging.info(*args)

    def warn(self, *args):
        logging.warning(*args)

    def debug(self, *args):
        logging.debug(*args)
