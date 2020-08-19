from sys import argv, exit as sysexit, stderr
from pathlib import Path
from PyPDF2 import PdfFileReader
from PyQt5.QtCore import QRect
from pymediainfo import MediaInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QSizePolicy

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


def get_result(path: str):
    return {
        'pdf_pages': get_total_pdf_pages(path),
        'pdf_documents': get_total_files(path, type="doc"),
        'video_seconds': get_total_video_seconds(path),
        'videos': get_total_files(path, type="vid"),
    }


def _separate_sections():
    print("~" * 42)


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


class Window(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.init_ui()

    def init_ui(self):
        welcome = Welcome()
        self.setCentralWidget(welcome)

        self.setWindowTitle("Study Planner")
        # self.setWindowIcon(QIcon("path here")))

        self.show()


class Welcome(QWidget):
    def __init__(self):
        super().__init__()
        self.info = QLabel("Choose an exam directory to get an estimation of the time required to study its contents.")
        self.choose_directory_button = QPushButton("Choose directory")
        self.choose_directory_button.clicked.connect(lambda: self.show_file_dialog())

        v_box = QVBoxLayout()
        v_box.addWidget(self.info)
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.choose_directory_button)
        h_box.addStretch()
        v_box.addLayout(h_box)
        self.setLayout(v_box)

    def show_file_dialog(self):
        FileDialog()


class FileDialog(QWidget):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.show_result_widget()

    def show_result_widget(self):
        LoadingScreen()
        path = str(QFileDialog.getExistingDirectory(self, "Choose directory"))
        ShowResult(path)


class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.loading_text = QLabel("Loading...")
        # TODO: add spinner from https://github.com/snowwlex/QtWaitingSpinner
        # self.loading_spinner = QtWaitingSpinner()
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.loading_text)
        h_box.addStretch()
        self.setLayout(h_box)

        window.takeCentralWidget()
        window.setCentralWidget(self)


class HLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("line")
        self.setGeometry(QRect(320, 150, 118, 3))
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class ShowResult(QWidget):
    def __init__(self, path: str):
        # noinspection PyArgumentList
        super().__init__()

        self.analysis = self.get_analysis(path)
        self.analysis_docs = QLabel(self.analysis[0])
        self.analysis_docs.setWordWrap(True)
        self.analysis_vids = QLabel(self.analysis[1])
        self.analysis_vids.setWordWrap(True)
        self.analysis_tot = QLabel(self.analysis[2])
        self.analysis_tot.setWordWrap(True)

        v_box = QVBoxLayout()
        v_box.addWidget(self.analysis_docs)
        v_box.addWidget(HLine())
        v_box.addWidget(self.analysis_vids)
        if len(self.analysis_tot.text()) > 0:
            v_box.addWidget(HLine())
            v_box.addWidget(self.analysis_tot)
        self.setLayout(v_box)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        window.takeCentralWidget()
        window.setCentralWidget(self)

    def get_analysis(self, path):
        result = get_result(path)
        analysis = get_work_amount_analysis(result['pdf_pages'],
                                            result['pdf_documents'],
                                            result['video_seconds'],
                                            result['videos'])
        return analysis


def main():
    app = QApplication(argv)
    global window
    window = Window()
    sysexit(app.exec_())


if __name__ == "__main__":
    main()
