from sys import stderr
from pathlib import Path
from typing import Tuple

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


def get_total_pdf_pages(path: str) -> Tuple[int, bool]:
    total_pages = 0
    read_error = False
    for f in Path(path).rglob("*.pdf"):
        try:
            total_pages += PdfFileReader(open(f, 'rb'), strict=False).getNumPages()
        except PdfReadError:
            read_error = True
    return total_pages, read_error


def get_total_files(path: str, type: str) -> int:
    if type == "doc":
        return len(list(Path(path).rglob("*.pdf")))
    elif type == "vid":
        tot = 0
        for ext in video_exts:
            tot += len(list(Path(path).rglob(f"*{ext}")))
        return tot


def get_total_video_seconds(path: str) -> float:
    return sum(MediaInfo.parse(f).tracks[0].duration for ext in video_exts for f in Path(path).rglob(f"*{ext}")) / 1000


def get_result(path: str):
    pdf_pages, pdf_read_error = get_total_pdf_pages(path)
    return {
        'pdf_pages': pdf_pages,
        'pdf_read_error': pdf_read_error,
        'pdf_documents': get_total_files(path, type="doc"),
        'video_seconds': get_total_video_seconds(path),
        'videos': get_total_files(path, type="vid"),
    }


def get_work_amount_analysis(pdf_pages: int, pdf_documents: int, video_seconds: float, videos: int):
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

    if video_seconds == 0:
        result[1] += "It seems there are no video lectures to watch in the given directories."
    else:
        result[1] += f"There are {_human_readable_time(video_seconds)} to watch in the given directories divided between " \
                     f"{videos} videos.\n" \
                     f"At 1.5x it will take you {_human_readable_time(video_seconds / 1.5)} to finish.\n" \
                     f"At 2x it will take you {_human_readable_time(video_seconds / 2)}.\n" \
                     f"Instead, accounting for pauses to take notes (0.75x), it will take you " \
                     f"{_human_readable_time(video_seconds / 0.75)}."

    if pdf_pages > 0 and video_seconds > 0:
        result[2] += f"In total, it will take you approximately {_human_readable_time(pdf_time + video_seconds)} " \
                     f"to study everything in the given directories.\n" \
                     f"Going very fast (20 seconds per page, watching videos at 2x) will take you " \
                     f"{_human_readable_time(pdf_pages * 20 + video_seconds / 2)}.\n" \
                     f"Taking your time to master the subject (2 minutes per page, watching videos at 0.75x) will take you " \
                     f"{_human_readable_time(pdf_pages * 120 + video_seconds / 0.75)}."

    return result