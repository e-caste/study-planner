from pathlib import Path
from sys import argv, exit as sysexit, platform
import sys
from typing import List

from PyQt5.QtCore import QRect, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QLineEdit, QDialog, QStackedWidget, QTreeView
from PyQt5.QtGui import QFont, QIcon

from backend import get_analysis
from waiting_spinner_widget import QtWaitingSpinner

DB_PATH = Path.joinpath(Path.home(), '.study_planner')
DB_FILE = str(Path.joinpath(DB_PATH, '_study_planner_db.txt'))
BTN_TITLE_TEXT = "Choose files and/or directories"


def get_last_dir():
    Path.mkdir(DB_PATH, exist_ok=True)
    if not Path(DB_FILE).exists():
        with open(DB_FILE, 'w') as f:
            f.write(str(Path.home()))
    with open(DB_FILE, 'r') as f:
        path = f.read()
        # if the user or the system has changed the contents of the file, it may not contain a valid path
        return path if Path(path).is_dir() else str(Path.home())


def set_last_dir(last_dir: str):
    with open(DB_FILE, 'w') as f:
        f.write(last_dir.strip())


class Analyser(QThread):
    analysis_signal = pyqtSignal(list)  # List[str]

    def __init__(self, paths: List[str]):
        QThread.__init__(self)
        self.paths = paths

    def run(self):
        self.analysis_signal.emit(get_analysis(self.paths))


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

        self.get_analysis_threaded()
        self.show_loading_screen()

    def show_loading_screen(self):
        self.setLayout(self.loading_screen)

    def get_analysis_threaded(self):
        self.analyser.analysis_signal.connect(self.init_ui)
        self.analyser.start()

    # https://stackoverflow.com/a/10439207
    def replace_layout(self, new_layout):
        QWidget().setLayout(self.layout())
        self.setLayout(new_layout)

    def init_ui(self, analysis):
        analysis_docs = QLabel(analysis[0])
        analysis_docs.setWordWrap(True)
        analysis_vids = QLabel(analysis[1])
        analysis_vids.setWordWrap(True)
        analysis_tot = QLabel(analysis[2])
        analysis_tot.setWordWrap(True)

        font_height = 15
        title_font = QFont()
        title_font.setPointSize(font_height)
        title_font.setBold(True)
        docs_title = QLabel("Documents")
        docs_title.setFont(title_font)
        vids_title = QLabel("Videos")
        vids_title.setFont(title_font)
        tot_title = QLabel("Total")
        tot_title.setFont(title_font)

        v_box = QVBoxLayout()
        v_box.addWidget(docs_title)
        v_box.addWidget(analysis_docs)
        v_box.addWidget(HLine())
        v_box.addWidget(vids_title)
        v_box.addWidget(analysis_vids)

        height = int(2/3 * analysis_docs.height() + 2 * font_height)
        if len(analysis_tot.text()) > 0:
            v_box.addWidget(HLine())
            v_box.addWidget(tot_title)
            v_box.addWidget(analysis_tot)
            height = int(analysis_docs.height() + 3 * 2 * font_height)

        choose_directory_button = QPushButton(BTN_TITLE_TEXT)
        choose_directory_button.clicked.connect(lambda: show_file_dialog())
        height += 20

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


def main():
    app = QApplication(argv)
    global window
    window = Window()
    global width
    width = window.width()
    sysexit(app.exec_())


if __name__ == "__main__":
    main()
