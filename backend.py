from sys import stderr
from pathlib import Path
from typing import Tuple, List, Callable
from threading import Thread
from queue import Queue  # https://stackoverflow.com/a/36926134
import json
from json import JSONDecodeError
from enum import Enum
from itertools import product

from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError
from pymediainfo import MediaInfo


def _get_all_possible_lowercase_uppercase_extension_combinations(strings: List[str]) -> List[str]:
    res = []
    for s in strings:
        res += map(''.join, product(*zip(s.upper(), s.lower())))
    return list(set(f".{ext}" for ext in res))


video_exts = _get_all_possible_lowercase_uppercase_extension_combinations(["mp4", "flv", "mov", "avi", "mkv"])
DB_PATH = Path.joinpath(Path.home(), '.study_planner')
DB_FILE = str(Path.joinpath(DB_PATH, '_study_planner_db.json'))


class Preference(Enum):
    last_dir = 'last_dir'
    docs_seconds = 'docs_seconds'
    vids_multiplier = 'vids_multiplier'
    day_hours = 'day_hours'


class PreferenceDefault(Enum):
    last_dir = str(Path.home())
    docs_seconds = 60
    vids_multiplier = 1.
    day_hours = 5


def get_preference(preference: Preference, default_value: PreferenceDefault, valid_condition: Callable):
    def write_default():
        with open(DB_FILE, 'w') as f:
            f.write(json.dumps({preference.value: default_value.value}))

    Path.mkdir(DB_PATH, exist_ok=True)
    if not Path(DB_FILE).exists():
        write_default()
    try:
        data = json.load(open(DB_FILE, 'r'))
    except JSONDecodeError:  # empty file
        write_default()
        return default_value.value
    if valid_condition(data):
        return data[preference.value]
    return default_value.value


def set_preference(preference: str, default_value, new_value):
    Path.mkdir(DB_PATH, exist_ok=True)
    if not Path(DB_FILE).exists():
        with open(DB_FILE, 'w') as f:
            f.write(json.dumps({preference: default_value}))
            return
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
        data[preference] = new_value
    with open(DB_FILE, 'w') as f:
        f.write(json.dumps(data))


def human_readable_time(seconds) -> str:
    if seconds < 0:
        print("An error occurred due to negative time being calculated. Please try again.", file=stderr)
        exit(-1)
    elif 0 <= seconds < 60:
        return f"{seconds} second(s)"
    elif 60 <= seconds < 3600:
        minutes = int(seconds // 60)
        remainder = int(seconds % 60)
        res = f"{minutes} minute(s)"
        if remainder != 0:
            res += f" and {remainder} second(s)"
        return res
    elif seconds >= 3600:
        hours = int(seconds // 3600)
        remainder = int(seconds % 3600)
        res = f"{hours} hour(s)"
        if remainder != 0:
            res += f" and {remainder // 60} minute(s)"
        return res


def _is_video_file(path: str) -> bool:
    return any([path.endswith(ext) for ext in video_exts])


def _get_thread_doc_files(path: str) -> int:
    tot = 0
    if Path(path).is_file():
        tot += 1
    elif Path(path).is_dir():
        tot += len(list(Path(path).rglob("*.pdf")))
    return tot


def _get_thread_vid_files(path: str) -> int:
    tot = 0
    if Path(path).is_file() and _is_video_file(path):
        tot += 1
    elif Path(path).is_dir():
        for ext in video_exts:
            tot += len(list(Path(path).rglob(f"*{ext}")))
    return tot


def _get_thread_pdf_pages(path: str) -> Tuple[int, bool]:
    pages, error = 0, False
    try:
        if Path(path).is_file() and path.endswith(".pdf"):
            pages += PdfFileReader(open(path, 'rb'), strict=False).getNumPages()
        elif Path(path).is_dir():
            for f in Path(path).rglob("*.pdf"):
                pages += PdfFileReader(open(f, 'rb'), strict=False).getNumPages()
    except (PdfReadError, Exception) as e:
        print(e)
        error = True
    return pages, error


def _get_thread_video_seconds(path: str) -> Tuple[float, bool]:
    seconds, error = 0., False
    try:
        if Path(path).is_file() and _is_video_file(path):
            seconds += MediaInfo.parse(path).tracks[0].duration
        elif Path(path).is_dir():
            for ext in video_exts:
                for f in Path(path).rglob(f"*{ext}"):
                    seconds += MediaInfo.parse(f).tracks[0].duration
    except (FileNotFoundError, IOError, RuntimeError, Exception) as e:
        print(e)
        error = True
    return seconds, error


def run_multithreaded(paths: List[str], callback: Callable, **kwargs):
    total, error, return_tuple = 0., False, False
    threads = []
    queue = Queue()
    if len(paths) == 1 and Path(paths[0]).is_dir():  # go one level deeper
        _paths = list(Path(paths[0]).glob("*"))
        if _paths:  # prevent crash for empty dirs
            paths = [str(p) for p in _paths]
    for path in paths:
        threads.append(Thread(target=lambda q, func, p: q.put(func(p)), args=(queue, callback, path)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for _ in range(len(threads)):
        res = queue.get()  # this is blocking, like await
        if isinstance(res, tuple):
            total += res[0]
            error |= res[1]
            return_tuple = True
        else:
            total += res
    if total == int(total):  # 1.0 == 1 but 1.2 != 1
        total = int(total)  # cast to int
    return (total, error) if return_tuple else total


def get_total_files(paths: List[str], type: str) -> int:
    if type == "doc":
        return run_multithreaded(paths, _get_thread_doc_files)
    elif type == "vid":
        return run_multithreaded(paths, _get_thread_vid_files)


def get_total_pdf_pages(paths: List[str]) -> Tuple[int, bool]:
    return run_multithreaded(paths, _get_thread_pdf_pages)


def get_total_video_seconds(paths: List[str]) -> Tuple[float, bool]:
    return run_multithreaded(paths, _get_thread_video_seconds)


def get_result(paths: List[str]) -> dict:
    pdf_pages, pdf_error = get_total_pdf_pages(paths)
    video_seconds, video_error = get_total_video_seconds(paths)
    return {
        'pdf_pages': pdf_pages,
        'pdf_error': pdf_error,
        'pdf_documents': get_total_files(paths, type="doc"),
        'video_seconds': video_seconds / 1000,
        'video_error': video_error,
        'videos': get_total_files(paths, type="vid"),
    }
