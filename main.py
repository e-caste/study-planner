from sys import argv, stderr
from pathlib import Path
from PyPDF2 import PdfFileReader
from cv2 import VideoCapture


def get_total_pdf_pages(path: str):
    pass


def get_total_video_seconds(path: str):
    pass


def main():
    if len(argv) == 0:
        paths = ["."]
    else:
        paths = [p for p in argv]

    result = {
        'pdf_pages': 0,
        'video_seconds': 0.,
    }
    for path in paths:
        result['pdf_pages'] += get_total_pdf_pages(path)
        result['video_seconds'] += get_total_video_seconds(path)

    print("stats here")


if __name__ == "__main__":
    main()
