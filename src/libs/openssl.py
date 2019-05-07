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
OpenSSL wrapper
"""

from os import makedirs
from os.path import exists
from subprocess import Popen


DIR_SEPARATOR = r"/"
LOG_SDTOUT = "/tmp/nova/ssl/log"
DEFAULT_SSL_CERTFILE = "cert.pem"
DEFAULT_SSL_KEYFILE = "key.pem"


def create_cmd(cert, key):
    return ["openssl", "req", "-x509", "-newkey", "rsa:4096", "-days", "365",
            "-nodes", "-keyout", key, "-out", cert,
            "-subj", "/C=NV/ST=NOVA/L=NOVA/O=NOVA/CN=NOVA"]


def create_path(output):
    dirs = output.split(DIR_SEPARATOR)
    filename = dirs.pop()
    filepath = DIR_SEPARATOR.join(dirs)
    if len(filepath) > 0 and not exists(filepath):
        makedirs(filepath)
    return output


def openssl(certfile, keyfile):
    if not isinstance(certfile, (str, unicode)):
        certfile = DEFAULT_SSL_CERTFILE
    if not isinstance(certfile, (str, unicode)):
        keyfile = DEFAULT_SSL_KEYFILE
    create_path(certfile)
    create_path(keyfile)
    create_path(LOG_SDTOUT)
    code = None
    cmd = create_cmd(certfile, keyfile)
    with open(LOG_SDTOUT, "wb") as log:
        proc = Popen(cmd, stdout=log, stderr=log)
        code = proc.wait()
    return code
