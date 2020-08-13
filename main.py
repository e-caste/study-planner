from sys import argv
from pathlib import Path
from PyPDF2 import PdfFileReader
from pymediainfo import MediaInfo


def get_total_pdf_pages(path: str):
    return sum(PdfFileReader(open(f, 'rb'), strict=False).getNumPages() for f in Path(path).rglob("*.pdf"))


def get_total_video_seconds(path: str):
    return sum(MediaInfo.parse(f).tracks[0].duration for ext in [".mp4", ".flv", ".mov"] for f in Path(path).rglob(f"*{ext}")) / 1000


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

    print(result)


if __name__ == "__main__":
    main()
