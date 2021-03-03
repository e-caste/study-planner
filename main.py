from pathlib import Path
from sys import argv, exit as sysexit, platform
import sys
from typing import List
from time import time
import json

from PyQt5.QtCore import QRect, pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QLineEdit, QDialog, QStackedWidget, QTreeView, QSlider
from PyQt5.QtGui import QFont, QIcon

from backend import get_result, human_readable_time
from waiting_spinner_widget import QtWaitingSpinner

DB_PATH = Path.joinpath(Path.home(), '.study_planner')
DB_FILE = str(Path.joinpath(DB_PATH, '_study_planner_db.json'))
BTN_TITLE_TEXT = "Choose files and/or directories"


def get_last_dir() -> str:
    Path.mkdir(DB_PATH, exist_ok=True)
    if not Path(DB_FILE).exists():
        with open(DB_FILE, 'w') as f:
            f.write(json.dumps({'last_dir': str(Path.home())}))
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
        # if the user or the system has changed the contents of the file, it may not contain a valid path
        if 'last_dir' in data and Path(data['last_dir']).is_dir():
            return data['last_dir']
        return str(Path.home())


def set_last_dir(last_dir: str):
    with open(DB_FILE, 'w') as f:
        f.write(json.dumps({'last_dir': last_dir.strip()}))


class Analyser(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, paths: List[str]):
        QThread.__init__(self)
        self.paths = paths

    def run(self):
        start = time()
        self.result_signal.emit(get_result(self.paths))
        print(f"Time taken to analyse the following paths:\n{self.paths}\n--> {time() - start} s")


class Window(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.init_ui()

    def init_ui(self):
        welcome = Welcome()
        self.setCentralWidget(welcome)

        self.setWindowTitle("Study Planner")
        # on Windows and GNU/Linux
        if not platform.startswith("darwin"):
            # see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path.cwd()
            self.setWindowIcon(QIcon(str(Path.joinpath(base_path, "icons", "icon_round.ico"))))

        self.show()


# def show_file_dialog(widget):
#     containing_layout = widget.parent().layout()
#     containing_layout.replaceWidget(widget, FileDialog(last_dir=get_last_dir()))

def show_file_dialog():
    FileDialog(last_dir=get_last_dir())


class Welcome(QWidget):
    def __init__(self, retry: bool = False):
        super().__init__()
        try_again = "You haven't selected any file or directory!\n\n" if retry else ""
        self.info = QLabel(f"{try_again}Choose an exam directory to get an estimation of the time required to "
                           f"study its contents.")
        self.choose_directory_button = QPushButton(BTN_TITLE_TEXT)
        self.choose_directory_button.clicked.connect(lambda: show_file_dialog())

        v_box = QVBoxLayout()
        v_box.addWidget(self.info)
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.choose_directory_button)
        h_box.addStretch()
        v_box.addLayout(h_box)
        self.setLayout(v_box)


class LoadingScreen(QVBoxLayout):
    def __init__(self, show_spinner: bool = True):
        super().__init__()
        self.loading_text = QLabel("Waiting for you to choose some files or directories...")
        self.loading_spinner = QtWaitingSpinner()

        if show_spinner:
            h_box_spinner = QHBoxLayout()
            h_box_spinner.addStretch()
            h_box_spinner.addWidget(self.loading_spinner)
            h_box_spinner.addStretch()
            self.addLayout(h_box_spinner)
            self.loading_spinner.start()
        else:
            h_box_text = QHBoxLayout()
            h_box_text.addStretch()
            h_box_text.addWidget(self.loading_text)
            h_box_text.addStretch()
            self.addLayout(h_box_text)


# see https://stackoverflow.com/a/64340482
def get_open_files_and_dirs(parent=None, caption='', directory='',
                            filter='', initial_filter='', options=None):
    def update_text():
        # update the contents of the line edit widget with the selected files
        selected = []
        for index in view.selectionModel().selectedRows():
            selected.append(index.data())
        line_edit.setText(",  ".join(selected))

    dialog = QFileDialog(parent, caption)
    dialog.setFileMode(dialog.ExistingFiles)
    if options:
        dialog.setOptions(options)
    dialog.setOption(dialog.DontUseNativeDialog, True)
    dialog.setOption(dialog.DontUseCustomDirectoryIcons, True)
    if directory:
        dialog.setDirectory(directory)
    if filter:
        dialog.setNameFilter(filter)
        if initial_filter:
            dialog.selectNameFilter(initial_filter)

    # by default, if a directory is opened in file listing mode,
    # QFileDialog.accept() shows the contents of that directory, but we
    # need to be able to "open" directories as we can do with files, so we
    # just override accept() with the default QDialog implementation which
    # will just return exec_()
    dialog.accept = lambda: QDialog.accept(dialog)

    # there are many item views in a non-native dialog, but the ones displaying
    # the actual contents are created inside a QStackedWidget; they are a
    # QTreeView and a QListView, and the tree is only used when the
    # viewMode is set to QFileDialog.Detail, which is not this case
    dialog.setViewMode(QFileDialog.Detail)
    stackedWidget = dialog.findChild(QStackedWidget)
    view = stackedWidget.findChild(QTreeView)
    view.selectionModel().selectionChanged.connect(update_text)

    line_edit = dialog.findChild(QLineEdit)
    # clear the line edit contents whenever the current directory changes
    dialog.directoryEntered.connect(lambda: line_edit.setText(""))

    dialog.exec_()
    return dialog.selectedFiles()


# TODO: show tree macOS style - this is surprisingly difficult, leaving as is for now
class FileDialog(QWidget):
    def __init__(self, last_dir: str):
        # noinspection PyArgumentList
        super().__init__()
        self.title = BTN_TITLE_TEXT
        self.last_dir = last_dir

        # TODO: fix this is not shown
        self.setLayout(LoadingScreen(show_spinner=False))
        self.show_result_widget()

    def show_result_widget(self):
        paths = get_open_files_and_dirs(caption=BTN_TITLE_TEXT,
                                        directory=self.last_dir)
        if not paths:
            window.takeCentralWidget()
            window.setCentralWidget(Welcome(retry=True))
        else:
            print(paths, str(Path(paths[0]).parent))
            set_last_dir(str(Path(paths[0]).parent))
            window.takeCentralWidget()
            window.setCentralWidget(ShowResult(paths))


class HLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("line")
        self.setGeometry(QRect(320, 150, 118, 3))
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class ShowResult(QWidget):
    def __init__(self, paths: List[str]):
        # noinspection PyArgumentList
        super().__init__()

        self.analyser = Analyser(paths)
        self.loading_screen = LoadingScreen(show_spinner=True)

        self.result = {
            'pdf_pages': 0,
            'pdf_error': False,
            'pdf_documents': 0,
            'video_seconds': 0,
            'video_error': False,
            'videos': 0,
        }

        # TODO: save values to preferences file
        self.docs_seconds = 60
        self.vids_multiplier = 1

        self.docs_slider = QSlider(orientation=Qt.Horizontal)
        self.vids_slider = QSlider(orientation=Qt.Horizontal)
        self.docs_slider.setMinimum(1)   # 10 seconds per slide
        self.docs_slider.setMaximum(60)  # 10 minutes per slide
        self.docs_slider.setValue(self.docs_seconds // 10)
        self.vids_slider.setMinimum(1)    # 0.1x -> 10 times longer
        self.vids_slider.setMaximum(50)   # 5x -> 1/20 of the length
        self.vids_slider.setValue(self.vids_multiplier * 10)
        self.docs_slider.valueChanged.connect(self.update_docs_seconds)
        self.vids_slider.valueChanged.connect(self.update_vids_multiplier)

        self.analysis_docs = QLabel("")
        self.analysis_docs.setWordWrap(True)
        self.analysis_vids = QLabel("")
        self.analysis_vids.setWordWrap(True)
        self.analysis_tot = QLabel("")
        self.analysis_tot.setWordWrap(True)

        self.get_analysis_threaded()
        self.show_loading_screen()

    def show_loading_screen(self):
        self.setLayout(self.loading_screen)

    def get_analysis_threaded(self):
        self.analyser.result_signal.connect(self.init_ui)
        self.analyser.start()

    # https://stackoverflow.com/a/10439207
    def replace_layout(self, new_layout):
        QWidget().setLayout(self.layout())
        self.setLayout(new_layout)

    def init_ui(self, result: dict):
        self.result = result

        self.update_analysis_labels()

        font_height = 15
        label_width = int(0.28 * width)
        title_font = QFont()
        title_font.setPointSize(font_height)
        title_font.setBold(True)
        docs_title = QLabel("Documents")
        docs_title.setFont(title_font)
        docs_title.setMinimumWidth(label_width)
        vids_title = QLabel("Videos")
        vids_title.setFont(title_font)
        vids_title.setMinimumWidth(label_width)
        tot_title = QLabel("Total")
        tot_title.setFont(title_font)

        h_box_docs = QHBoxLayout()
        h_box_docs.addWidget(docs_title)
        h_box_docs.addStretch()
        h_box_docs.addWidget(QLabel("Time per page"))
        h_box_docs.addWidget(self.docs_slider)
        h_box_vids = QHBoxLayout()
        h_box_vids.addWidget(vids_title)
        h_box_vids.addStretch()
        h_box_vids.addWidget(QLabel("Video speed"))
        h_box_vids.addWidget(self.vids_slider)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box_docs)
        v_box.addWidget(self.analysis_docs)
        v_box.addWidget(HLine())
        v_box.addLayout(h_box_vids)
        v_box.addWidget(self.analysis_vids)

        height = int(1/3 * self.analysis_docs.height() + 2 * font_height)
        if len(self.analysis_tot.text()) > 0:
            v_box.addWidget(HLine())
            v_box.addWidget(tot_title)
            v_box.addWidget(self.analysis_tot)
            height = int(2/3 * self.analysis_docs.height() + 3 * font_height)

        choose_directory_button = QPushButton(BTN_TITLE_TEXT)
        choose_directory_button.clicked.connect(lambda: show_file_dialog())

        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(choose_directory_button)
        h_box.addStretch()
        v_box.addLayout(h_box)

        self.replace_layout(v_box)

        window.takeCentralWidget()
        window.setCentralWidget(self)

        # height = 160 * number_of_widgets
        window.resize(width, height)

    def update_docs_seconds(self, seconds: int):
        self.docs_seconds = seconds * 10
        self.update_analysis_labels()

    def update_vids_multiplier(self, multiplier: int):
        self.vids_multiplier = multiplier / 10
        self.update_analysis_labels()

    def update_analysis_labels(self):
        docs_text, vids_text, tot_text = "", "", ""

        if self.result['pdf_pages'] == 0:
            # the initial and ending newlines are used to not cut off the QLabel in ShowResult
            docs_text += "\nIt seems there are no pdfs to study in the given directories.\n"
            self.docs_slider.setHidden(True)
        else:
            docs_time = self.docs_seconds * self.result['pdf_pages']
            docs_text += f"\nThere are {self.result['pdf_pages']} pdf pages to study in the given directories " \
                         f"spanning {self.result['pdf_documents']} files.\n" \
                         f"At {human_readable_time(self.docs_seconds)} per page, it will take you " \
                         f"{human_readable_time(docs_time)} to study these " \
                         f"documents.\n"
        if self.result['pdf_error']:
            docs_text += "\nIt seems some PDF documents could not be opened correctly, they have been skipped.\n"

        if self.result['video_seconds'] == 0:
            vids_text += "\nIt seems there are no video lectures to watch in the given directories.\n"
            self.vids_slider.setHidden(True)
        else:
            vids_time = self.result['video_seconds'] * self.vids_multiplier
            vids_text += f"\nThere are {human_readable_time(self.result['video_seconds'])} to watch in the given " \
                         f"directories divided between {self.result['videos']}.\n" \
                         f"At {self.vids_multiplier}x it will take you " \
                         f"{human_readable_time(vids_time)} to finish.\n"
        if self.result['video_error']:
            vids_text += "\nIt seems some video files could not be opened correctly, they have been skipped.\n"

        self.analysis_docs.setText(docs_text)
        self.analysis_vids.setText(vids_text)

        if self.result['pdf_pages'] > 0 and self.result['video_seconds'] > 0:
            tot_text += f"\nIn total, it will take you {human_readable_time(docs_time + vids_time)} to study everything" \
                        f" in the given directories.\n"
            self.analysis_tot.setText(tot_text)


def main():
    app = QApplication(argv)
    global window
    window = Window()
    global width
    width = window.width()
    sysexit(app.exec_())


if __name__ == "__main__":
    main()
