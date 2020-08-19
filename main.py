from sys import argv, exit as sysexit
from backend import get_result, get_work_amount_analysis
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QSizePolicy


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
