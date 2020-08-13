from sys import argv, stderr
from pathlib import Path
from PyPDF2 import PdfFileReader
from pymediainfo import MediaInfo


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


def get_total_video_seconds(path: str) -> float:
    return sum(MediaInfo.parse(f).tracks[0].duration for ext in [".mp4", ".flv", ".mov"] for f in Path(path).rglob(f"*{ext}")) / 1000


def print_work_amount_analysis(pdf_pages: int, video_seconds: float):
    if pdf_pages == 0:
        print("It seems there are no pdfs to study in the given directories.")
    else:
        pdf_time = pdf_pages * 120
        print(f"There are {pdf_pages} pdf pages to study in the given directories.\n"
              f"At 2 minutes per page, it will take you {_human_readable_time(pdf_time)} to study these documents.")

    print("~" * 42)

    if video_seconds == 0:
        print("It seems there are no video lectures to watch in the given directories.")
    else:
        print(f"There are {_human_readable_time(video_seconds)} to watch in the given directories.\n"
              f"At 1.5x it will take you {_human_readable_time(video_seconds / 1.5)} to finish.\n"
              f"At 2x it will take you {_human_readable_time(video_seconds / 2)}.\n"
              f"Instead, accounting for pauses to take notes (0.75x), it will take you "
              f"{_human_readable_time(video_seconds / 0.75)}.")

    if pdf_pages > 0 and video_seconds > 0:
        print("~" * 42)
        print(f"In total, it will take you approximately {_human_readable_time(pdf_time + video_seconds)} "
              f"to study everything in the given directories.")

def main():
    if len(argv) == 0:
        paths = ["."]
    else:
        paths = [p for p in argv[1:]]

    result = {
        'pdf_pages': 0,
        'video_seconds': 0.,
    }
    for path in paths:
        result['pdf_pages'] += get_total_pdf_pages(path)
        result['video_seconds'] += get_total_video_seconds(path)

    print_work_amount_analysis(result['pdf_pages'], result['video_seconds'])


if __name__ == "__main__":
    main()
