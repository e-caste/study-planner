from sys import stderr
from pathlib import Path
from typing import Tuple, List, Callable
from threading import Thread
from queue import Queue  # https://stackoverflow.com/a/36926134

from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError
from pymediainfo import MediaInfo


video_exts = [".mp4", ".flv", ".mov", ".avi"]


def _human_readable_time(seconds) -> str:
    if seconds < 0:
        print("An error occurred due to negative time being calculated. Please try again.", file=stderr)
        exit(-1)
    elif 0 <= seconds < 60:
        return f"{seconds} second(s)"
    elif 60 <= seconds < 3600:
        return f"{int(seconds / 60)} minute(s)"
    elif seconds >= 3600:
        hours = int(seconds / 3600)
        return f"{hours} hour(s) and {int((seconds - hours * 3600) / 60)} minute(s)"


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


def run_multithreaded(paths: List[str], callback: Callable, **kwargs):
    total, error, return_tuple = 0., False, False
    threads = []
    queue = Queue()
    if len(paths) == 1 and Path(paths[0]).is_dir():  # go one level deeper
        paths = [str(p) for p in Path(paths[0]).glob("*")]
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


def get_total_pdf_pages(paths: List[str]) -> Tuple[int, bool]:
    return run_multithreaded(paths, _get_thread_pdf_pages)


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


def get_work_amount_analysis(pdf_pages: int,
                             pdf_error: bool,
                             pdf_documents: int,
                             video_seconds: float,
                             video_error: bool,
                             videos: int):
    result = ["", "", ""]

    if pdf_pages == 0:
        result[0] += "It seems there are no pdfs to study in the given directories."
    else:
        pdf_time = pdf_pages * 120
        # the initial and ending newlines are used to not cut off the QLabel in ShowResult
        result[0] += f"\nThere are {pdf_pages} pdf pages to study in the given directories spanning {pdf_documents} files.\n" \
                     f"At 1 minute per page, it will take you {_human_readable_time(pdf_pages * 60)} to study these " \
                     f"documents.\n" \
                     f"At 2 minutes per page, it will take you {_human_readable_time(pdf_time)} to study these documents.\n" \
                     f"Instead, skimming very quickly (20 seconds per page) will take you " \
                     f"{_human_readable_time(pdf_pages * 20)}.\n"

    if pdf_error:
        result[0] += "\nIt seems some PDF documents could not be opened correctly, they have been skipped.\n"

    if video_seconds == 0:
        result[1] += "It seems there are no video lectures to watch in the given directories."
    else:
        result[1] += f"There are {_human_readable_time(video_seconds)} to watch in the given directories divided between " \
                     f"{videos} videos.\n" \
                     f"At 1.5x it will take you {_human_readable_time(video_seconds / 1.5)} to finish.\n" \
                     f"At 2x it will take you {_human_readable_time(video_seconds / 2)}.\n" \
                     f"Instead, accounting for pauses to take notes (0.75x), it will take you " \
                     f"{_human_readable_time(video_seconds / 0.75)}.\n"

    if video_error:
        result[1] += "\nIt seems some video files could not be opened correctly, they have been skipped.\n"

    if pdf_pages > 0 and video_seconds > 0:
        result[2] += f"In total, it will take you approximately {_human_readable_time(pdf_time + video_seconds)} " \
                     f"to study everything in the given directories.\n" \
                     f"Going very fast (20 seconds per page, watching videos at 2x) will take you " \
                     f"{_human_readable_time(pdf_pages * 20 + video_seconds / 2)}.\n" \
                     f"Taking your time to master the subject (2 minutes per page, watching videos at 0.75x) will take you " \
                     f"{_human_readable_time(pdf_pages * 120 + video_seconds / 0.75)}.\n"

    # add second space after comma so that UI displays correctly
    return [text.replace(", ", ",  ") for text in result]


def get_analysis(paths: List[str]):
    result = get_result(paths)
    analysis = get_work_amount_analysis(result['pdf_pages'],
                                        result['pdf_error'],
                                        result['pdf_documents'],
                                        result['video_seconds'],
                                        result['video_error'],
                                        result['videos'])
    return analysis
