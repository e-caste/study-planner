from sys import argv, stderr
from pathlib import Path
from PyPDF2 import PdfFileReader
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


def get_total_pdf_pages(path: str) -> int:
    return sum(PdfFileReader(open(f, 'rb'), strict=False).getNumPages() for f in Path(path).rglob("*.pdf"))


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


def _separate_sections():
    print("~" * 42)


def print_work_amount_analysis(pdf_pages: int, pdf_documents: int, video_seconds: float, videos: int):
    print()

    if pdf_pages == 0:
        print("It seems there are no pdfs to study in the given directories.")
    else:
        pdf_time = pdf_pages * 120
        print(f"There are {pdf_pages} pdf pages to study in the given directories spanning {pdf_documents} files.\n"
              f"At 1 minute per page, it will take you {_human_readable_time(pdf_pages * 60)} to study these "
              f"documents.\n"
              f"At 2 minutes per page, it will take you {_human_readable_time(pdf_time)} to study these documents.\n"
              f"Instead, skimming very quickly (20 seconds per page) will take you "
              f"{_human_readable_time(pdf_pages * 20)}.")

    _separate_sections()

    if video_seconds == 0:
        print("It seems there are no video lectures to watch in the given directories.")
    else:
        print(f"There are {_human_readable_time(video_seconds)} to watch in the given directories divided between "
              f"{videos} videos.\n"
              f"At 1.5x it will take you {_human_readable_time(video_seconds / 1.5)} to finish.\n"
              f"At 2x it will take you {_human_readable_time(video_seconds / 2)}.\n"
              f"Instead, accounting for pauses to take notes (0.75x), it will take you "
              f"{_human_readable_time(video_seconds / 0.75)}.")

    if pdf_pages > 0 and video_seconds > 0:
        _separate_sections()
        print(f"In total, it will take you approximately {_human_readable_time(pdf_time + video_seconds)} "
              f"to study everything in the given directories.\n"
              f"Going very fast (20 seconds per page, watching videos at 2x) will take you "
              f"{_human_readable_time(pdf_pages * 20 + video_seconds / 2)}.\n"
              f"Taking your time to master the subject (2 minutes per page, watching videos at 0.75x) will take you "
              f"{_human_readable_time(pdf_pages * 120 + video_seconds / 0.75)}.")


def main():
    if len(argv) == 0:
        paths = ["."]
    else:
        paths = argv[1:]

    result = {
        'pdf_pages': 0,
        'pdf_documents': 0,
        'video_seconds': 0.,
        'videos': 0,
    }
    for path in paths:
        result['pdf_pages'] += get_total_pdf_pages(path)
        result['pdf_documents'] += get_total_files(path, type="doc")
        result['video_seconds'] += get_total_video_seconds(path)
        result['videos'] += get_total_files(path, type="vid")

    print_work_amount_analysis(result['pdf_pages'],
                               result['pdf_documents'],
                               result['video_seconds'],
                               result['videos'])


if __name__ == "__main__":
    main()
