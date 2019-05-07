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
Helper functions and constants.
"""

from traceback import print_tb
from sys import exc_info
from urllib2 import urlopen, HTTPError, URLError
from datetime import datetime
from urlparse import urlparse
from os import path, makedirs, environ, remove
from time import time, ctime
from re import sub

from consts import MIN_VALID_NVS, NOVA_DEBUG, NOVA_DB, NOVA_TMP


def nicefy(func, *args, **kwargs):
    def wrapper(*args, **kwargs):
        nice_func = None
        try:
            nice_func = func(*args, **kwargs)
        except KeyboardInterrupt:
            pass
        except Exception as ErrorException:
            if environ.get(NOVA_DEBUG) is not None:
                _, _, tb = exc_info()
                print_tb(tb)
            raise ErrorException
        return nice_func
    return wrapper


def parse_url(url):
    try:
        parser = urlparse(url)
        dir_ = parser.netloc
        page = sub(r"[\W]", "_", parser.path)
    except Exception:
        raise TypeError(r"Cannot parse URI: invalid resource")
    return dir_, page


def save_as(data, filename, filepath=None, root_dir=None, mode="wb"):
    if root_dir is not None:
        if root_dir.endswith("/"):
            root_dir = root_dir[-1]
        if filepath.startswith("/"):
            filepath = filepath[1]
        filepath = r"{}/{}".format(root_dir, filepath)
    if not path.exists(filepath):
        makedirs(filepath)
    with open(r"{}/{}".format(filepath, filename), mode) as file_:
        file_.write(data)
    return filename, filepath


def save_file(page, filetype, dirpath, data, root_dir, mode="wb"):
    now = datetime.now().strftime(r"%Y-%m-%d")
    timestamp = int(time())
    if page.startswith("_"):
        page = page.lstrip("_")
    if page == r"":
        page = "NA"
    filename = r"{}_{}.{}".format(timestamp, page, filetype)
    filepath = r"{}/{}".format(now, dirpath)
    return save_as(data, filename, filepath, root_dir)


def save_data(data, uri, filetype, root_dir=None):
    dirpath, page = parse_url(uri)
    return save_file(page, filetype, dirpath, data, root_dir)


def save_nvs(data, root_dir=None):
    if len(data) == 0:
        raise ValueError(r"Unexpected zero length data")
    if len(data) <= MIN_VALID_NVS:
        return None
    return save_data("\n".join(data), data[0], "nvs", root_dir)


def save_html(data, url, root_dir=None):
    if data is None:
        raise ValueError(r"Unexpected non-string empty data")
    return save_data(data.encode('utf8'), url, "html", root_dir)


def create_nvs_file(dirpath, page, root_dir=None):
    return save_file(page, "nvs", dirpath, u"", root_dir)


def update_nvs_session(message, filename, filepath):
    if message is None:
        raise ValueError(r"Unexpected non-string value")
    message += "\n"
    return save_as(message, filename, filepath, mode="a")


def path_exists(filepath):
    if isinstance(filepath, (str, unicode)):
        return path.exists(filepath)
    return False


def get_db_dir():
    return environ.get(NOVA_DB)


def get_db_meta(db=None):
    if db is None:
        db = get_db_dir()
    try:
        created_date = ctime(path.getctime(db))
        modified_date = ctime(path.getmtime(db))
    except:
        created_date, modified_date = "n/a", "n/a"
    return type("DBMeta", (object,), {
        "file": db,
        "missing": not path_exists(db),
        "created_date": created_date,
        "modified_date": modified_date,
    })


def check_url(url):
    try:
        urlopen(url)
    except HTTPError as e:
        return e.reason
    except URLError as e:
        return e.reason
    except Exception as e:
        return e.reason
    return None


def timestamp_date(ts, div=1000.):
    if isinstance(div, (int, float)) and div > 0:
        return datetime.utcfromtimestamp(int(ts)/div).strftime("%Y-%m-%d %H:%M:%S")
    raise ValueError("Avoiding an invalid division")


def lock_session():
    return "{}/session_{}.lock".format(NOVA_TMP, time())


def read_session(session):
    with open(session) as ses:
        return [s for s in ses.read().split("\n") if s]
    return []


def merge_session(nvs_session_lock, delete_sessions=True):
    if not path_exists(nvs_session_lock):
        return None
    def last_time(session):
        last_event = session[-1]
        try:
            ev = last_event.split(",")
            last_timestamp = int(ev[1])
        except:
            last_timestamp = 0
        return last_timestamp
    sessions = read_session(nvs_session_lock)
    nvs_file = sessions.pop(0)
    first_ses = read_session(nvs_file)
    last_timestamp = last_time(first_ses)
    nvs = "\n".join(first_ses)
    for s in sessions:
        ses, ts = [], last_timestamp
        for event in read_session(s)[4:]:
            ev = event.split(",")
            ts = int(ev[1]) + last_timestamp
            ev[1] = str(ts)
            ses.append(",".join(ev))
        last_timestamp = ts
        if len(ses) > 0:
            nvs += "\n" + "\n".join(ses)
    with open(nvs_file, "w") as file_:
        file_.write(nvs)
    if delete_sessions:
        remove(nvs_session_lock)
        [remove(s) for s in sessions if path_exists(s)]
    return nvs_file


def track_session(session_list, session_file):
    session_path = "/".join(session_list[::-1]) + "\n"
    with open(session_file, "a") as file_:
        file_.write(session_path)
