from sys import argv, exit as sysexit
import os
from pathlib import Path

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QSizePolicy, QLineEdit, QDialog, QStackedWidget, QTreeView

from backend import get_result, get_work_amount_analysis

DB_FILE = "_study_planner_db.txt"
BTN_TITLE_TEXT = "Choose files and/or directories"


def get_last_dir():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            f.write(str(Path.home()))
    with open(DB_FILE, 'r') as f:
        return f.read()


def set_last_dir(last_dir: str):
    with open(DB_FILE, 'w') as f:
        f.write(last_dir.strip())


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
    def __init__(self, retry: bool = False):
        super().__init__()
        try_again = "You haven't selected any file or directory!\n\n" if retry else ""
        self.info = QLabel(f"{try_again}Choose an exam directory to get an estimation of the time required to "
                           f"study its contents.")
        self.choose_directory_button = QPushButton(BTN_TITLE_TEXT)
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
        FileDialog(last_dir=get_last_dir())


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

        self.show_result_widget()

    def show_result_widget(self):
        LoadingScreen()
        paths = get_open_files_and_dirs(caption=BTN_TITLE_TEXT,
                                        directory=self.last_dir)
        if not paths:
            window.takeCentralWidget()
            window.setCentralWidget(Welcome(retry=True))
        else:
            print(paths, str(Path(paths[0]).parent))
            set_last_dir(str(Path(paths[0]).parent))
            # ShowResult(paths)


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
        height = int(2/3 * self.analysis_docs.height())
        if len(self.analysis_tot.text()) > 0:
            v_box.addWidget(HLine())
            v_box.addWidget(self.analysis_tot)
            height = int(self.analysis_docs.height())
        # self.analysis_docs.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setLayout(v_box)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        window.takeCentralWidget()
        window.setCentralWidget(self)

        # height = 160 * number_of_widgets
        window.resize(window.width(), height)

    def get_analysis(self, path):
        result = get_result(path)
        analysis = get_work_amount_analysis(result['pdf_pages'],
                                            result['pdf_read_error'],
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
