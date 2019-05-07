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
Simple threading wrapper for multiprocessing.
"""

from multiprocessing import Process, Queue


class Worker(object):

    queue = Queue()

    def __init__(self, func, *args):
        self.func = func
        self.args = args
        self.proc = Process(target=self.func, args=self.args, name=func.func_name)

    def start(self):
        self.proc.start()

    def join(self):
        self.proc.join()

    def stop(self):
        self.proc.terminate()

    @classmethod
    def catch(cls, item):
        return cls.queue.put(item)

    @classmethod
    def listen(cls):
        return cls.queue.get()

    @classmethod
    def close(cls):
        cls.queue.close()
        cls.queue.join_thread()
