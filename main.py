from pathlib import Path
from sys import argv, exit as sysexit, platform
import sys
from typing import List
from time import time
from math import ceil
from contextlib import redirect_stderr

from PyQt5.QtCore import QRect, pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, \
    QPushButton, QFrame, QLineEdit, QDialog, QStackedWidget, QTreeView, QSlider
from PyQt5.QtGui import QFont, QIcon, QCloseEvent, QPalette, QColor
import requests

from backend import get_result, Preference, PreferenceDefault, get_preference, set_preference, \
    DB_PATH, CURRENT_RELEASE
from waiting_spinner_widget import QtWaitingSpinner
from translations import Translator


class Analyser(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self, paths: List[str]):
        QThread.__init__(self)
        self.paths = paths

    def run(self):
        start = time()
        self.result_signal.emit(get_result(self.paths))
        print(f"Time taken to analyse the following paths:\n{self.paths}\n--> {time() - start} s")


class ReleaseFetcher(QThread):
    # only emitted if there is a new release
    new_release_signal = pyqtSignal(str)
    new_release = None  # cache to prevent spamming HTTP requests

    def run(self):
        if self.new_release:
            self.new_release_signal.emit(self.new_release)
        try:
            res = requests.get("https://api.github.com/repos/e-caste/study-planner/releases/latest")
            latest_release = res.json()['tag_name'] if 'tag_name' in res.json() else None
            if latest_release:
                is_new_release = latest_release > CURRENT_RELEASE  # string comparison
                self.new_release = latest_release if is_new_release else CURRENT_RELEASE
                self.new_release_signal.emit(self.new_release)
                print(f"New release found: {self.new_release}" if is_new_release else "Already on latest release.")
        except Exception as e:
            print(e, file=sys.stderr)


release_fetcher = ReleaseFetcher()


def fetch_latest_release():
    release_fetcher.new_release_signal.connect(_add_link_to_new_release)
    release_fetcher.start()


def _add_link_to_new_release(new_release: str):
    if new_release == CURRENT_RELEASE or window.centralWidget().showing_new_release:
        return
    new_release_label = QLabel(t.translate('new_release', new_release, CURRENT_RELEASE))
    new_release_label.setOpenExternalLinks(True)
    window.centralWidget().layout().addWidget(new_release_label)
    window.resize(window.width(), window.height() + 40)
    window.centralWidget().showing_new_release = True


class Window(QMainWindow):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.dark_mode_enabled = get_preference(Preference.dark_mode,
                                                PreferenceDefault.dark_mode,
                                                lambda data: Preference.dark_mode.value in data
                                                             and isinstance(data[Preference.dark_mode.value], bool))
        self.welcome = Welcome()
        self.init_ui()

    # save preferences to file before closing the program
    def closeEvent(self, event: QCloseEvent):
        if isinstance(self.centralWidget(), ShowResult):
            save_slider_preferences(self.centralWidget())
        set_preference(Preference.dark_mode.value,
                       PreferenceDefault.dark_mode.value,
                       window.dark_mode_enabled)
        event.accept()

    def init_ui(self):
        self.setCentralWidget(self.welcome)

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
        fetch_latest_release()
        _set_fusion_dark_mode(self.dark_mode_enabled)


# def show_file_dialog(widget):
#     containing_layout = widget.parent().layout()
#     containing_layout.replaceWidget(widget, FileDialog(last_dir=get_last_dir()))

def show_file_dialog():
    FileDialog(last_dir=get_preference(Preference.last_dir,
                                       PreferenceDefault.last_dir,
                                       lambda data: Preference.last_dir.value in data
                                                    and Path(data[Preference.last_dir.value]).is_dir()))


class Welcome(QWidget):
    def __init__(self, retry: bool = False):
        super().__init__()
        self.showing_new_release = False
        try_again = t.translate('no_files_selected') if retry else ""
        self.info = QLabel(t.translate('starting_text', try_again))
        self.choose_directory_button = QPushButton(t.translate('choose_button'))
        self.choose_directory_button.clicked.connect(lambda: show_file_dialog())
        self.toggle_dark_mode_button = QPushButton(t.translate('dark_mode'))
        self.toggle_dark_mode_button.clicked.connect(lambda: toggle_dark_mode())

        v_box = QVBoxLayout()
        v_box.addWidget(self.info)
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.choose_directory_button)
        if not platform.startswith("darwin"):
            h_box.addWidget(self.toggle_dark_mode_button)
        h_box.addStretch()
        v_box.addLayout(h_box)
        self.setLayout(v_box)


class LoadingScreen(QVBoxLayout):
    def __init__(self, show_spinner: bool = True):
        super().__init__()
        self.loading_text = QLabel(t.translate('waiting'))
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
        self.title = t.translate('choose_button')
        self.last_dir = last_dir

        # TODO: fix this is not shown
        self.setLayout(LoadingScreen(show_spinner=False))
        self.show_result_widget()

    def show_result_widget(self):
        paths = get_open_files_and_dirs(caption=self.title,
                                        directory=self.last_dir)
        if not paths:
            window.takeCentralWidget()
            window.setCentralWidget(Welcome(retry=True))
        else:
            print(paths, str(Path(paths[0]).parent))
            set_preference(Preference.last_dir.value,
                           PreferenceDefault.last_dir.value,
                           str(Path(paths[0]).parent))
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
        self.showing_new_release = False

        self.result = {
            'pdf_pages': 0,
            'pdf_error': False,
            'pdf_documents': 0,
            'video_seconds': 0,
            'video_error': False,
            'videos': 0,
        }

        self.docs_seconds = get_preference(Preference.docs_seconds,
                                           PreferenceDefault.docs_seconds,
                                           lambda data: Preference.docs_seconds.value in data
                                                        and isinstance(data[Preference.docs_seconds.value], int)
                                                        and 10 <= data[Preference.docs_seconds.value] <= 600)
        self.vids_multiplier = get_preference(Preference.vids_multiplier,
                                              PreferenceDefault.vids_multiplier,
                                              lambda data: Preference.vids_multiplier.value in data
                                                           and (isinstance(data[Preference.vids_multiplier.value], float)
                                                                or isinstance(data[Preference.vids_multiplier.value], int))
                                                           and 0.1 <= data[Preference.vids_multiplier.value] <= 5)
        self.day_hours = get_preference(Preference.day_hours,
                                        PreferenceDefault.day_hours,
                                        lambda data: Preference.day_hours.value in data
                                                     and (isinstance(data[Preference.day_hours.value], int))
                                                     and 1 <= data[Preference.day_hours.value] <= 24)

        self.docs_slider = QSlider(orientation=Qt.Horizontal)
        self.vids_slider = QSlider(orientation=Qt.Horizontal)
        self.prep_slider = QSlider(orientation=Qt.Horizontal)
        self.docs_slider.setMinimum(1)   # 10 seconds per slide
        self.docs_slider.setMaximum(60)  # 10 minutes per slide
        self.docs_slider.setValue(self.docs_seconds // 10)
        self.vids_slider.setMinimum(1)    # 0.1x -> 10 times longer
        self.vids_slider.setMaximum(50)   # 5x -> 1/5 of the length
        self.vids_slider.setValue(int(self.vids_multiplier * 10))
        self.prep_slider.setMinimum(1)    # 1 hour per day
        self.prep_slider.setMaximum(24)   # 24 hours per day
        self.prep_slider.setValue(self.day_hours)
        self.docs_slider.valueChanged.connect(self.update_docs_seconds)
        self.vids_slider.valueChanged.connect(self.update_vids_multiplier)
        self.prep_slider.valueChanged.connect(self.update_day_hours)

        slider_label_font = QFont()
        slider_label_font.setItalic(True)
        self.docs_slider_label = QLabel(t.translate('time_per_page'))
        self.docs_slider_label.setFont(slider_label_font)
        self.vids_slider_label = QLabel(t.translate('video_speed'))
        self.vids_slider_label.setFont(slider_label_font)
        self.prep_slider_label = QLabel(t.translate('hours_per_day'))
        self.prep_slider_label.setFont(slider_label_font)

        self.analysis_docs = QLabel("")
        self.analysis_docs.setWordWrap(True)
        self.analysis_vids = QLabel("")
        self.analysis_vids.setWordWrap(True)
        self.analysis_tot = QLabel("")
        self.analysis_tot.setWordWrap(True)
        self.analysis_prep = QLabel("")
        self.analysis_prep.setWordWrap(True)

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
        docs_title = QLabel(t.translate('documents'))
        docs_title.setFont(title_font)
        docs_title.setMinimumWidth(label_width)
        vids_title = QLabel(t.translate('videos'))
        vids_title.setFont(title_font)
        vids_title.setMinimumWidth(label_width)
        tot_title = QLabel(t.translate('total'))
        tot_title.setFont(title_font)
        prep_title = QLabel(t.translate('preparation'))
        prep_title.setFont(title_font)
        prep_title.setMinimumWidth(label_width)

        h_box_docs = QHBoxLayout()
        h_box_docs.addWidget(docs_title)
        h_box_docs.addStretch()
        h_box_docs.addWidget(self.docs_slider_label)
        h_box_docs.addWidget(self.docs_slider)
        h_box_vids = QHBoxLayout()
        h_box_vids.addWidget(vids_title)
        h_box_vids.addStretch()
        h_box_vids.addWidget(self.vids_slider_label)
        h_box_vids.addWidget(self.vids_slider)
        h_box_prep = QHBoxLayout()
        h_box_prep.addWidget(prep_title)
        h_box_prep.addStretch()
        h_box_prep.addWidget(self.prep_slider_label)
        h_box_prep.addWidget(self.prep_slider)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box_docs)
        v_box.addWidget(self.analysis_docs)
        v_box.addWidget(HLine())
        v_box.addLayout(h_box_vids)
        v_box.addWidget(self.analysis_vids)

        height = int(1/2 * self.analysis_docs.height() + 2 * font_height)
        if len(self.analysis_tot.text()) > 0:
            v_box.addWidget(HLine())
            v_box.addWidget(tot_title)
            v_box.addWidget(self.analysis_tot)
            height += int(1/4 * self.analysis_docs.height() + font_height)

        if self.result['pdf_pages'] > 0 or self.result['video_seconds'] > 0:
            v_box.addWidget(HLine())
            v_box.addLayout(h_box_prep)
            v_box.addWidget(self.analysis_prep)
            height += int(1/4 * self.analysis_docs.height() + font_height)

        choose_directory_button = QPushButton(t.translate('choose_button'))
        choose_directory_button.clicked.connect(self.click_directory_button)

        toggle_dark_mode_button = QPushButton(t.translate('dark_mode'))
        toggle_dark_mode_button.clicked.connect(lambda: toggle_dark_mode())

        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(choose_directory_button)
        if not platform.startswith("darwin"):
            h_box.addWidget(toggle_dark_mode_button)
        h_box.addStretch()
        v_box.addLayout(h_box)

        self.replace_layout(v_box)

        window.takeCentralWidget()
        window.setCentralWidget(self)

        # height = 160 * number_of_widgets
        window.resize(width, height)

        fetch_latest_release()

    def update_docs_seconds(self, seconds: int):
        self.docs_seconds = seconds * 10
        self.update_analysis_labels()

    def update_vids_multiplier(self, multiplier: int):
        self.vids_multiplier = multiplier / 10
        self.update_analysis_labels()

    def update_day_hours(self, hours: int):
        self.day_hours = hours
        self.update_analysis_labels()

    def update_analysis_labels(self):
        docs_text, vids_text, tot_text, prep_text = "", "", "", ""
        docs_time, vids_time = 0, 0

        if self.result['pdf_pages'] == 0:
            # the ending newlines are used to not cut off the QLabel in ShowResult
            docs_text += t.translate('no_docs')
            self.docs_slider.setHidden(True)
            self.docs_slider_label.setHidden(True)
        else:
            docs_time = self.docs_seconds * self.result['pdf_pages']
            docs_text += t.translate('docs_text',
                                     self.result['pdf_pages'],
                                     self.result['pdf_documents'],
                                     t.human_readable_time(self.docs_seconds),
                                     t.human_readable_time(docs_time)).replace("\n", "<br>")
        if self.result['pdf_error']:
            docs_text += t.translate('pdf_error')

        if self.result['video_seconds'] == 0:
            vids_text += t.translate('no_videos')
            self.vids_slider.setHidden(True)
            self.vids_slider_label.setHidden(True)
        else:
            vids_time = self.result['video_seconds'] / self.vids_multiplier
            vids_text += t.translate('vids_text',
                                     t.human_readable_time(self.result['video_seconds']),
                                     self.result['videos'],
                                     self.vids_multiplier,
                                     t.human_readable_time(vids_time)).replace("\n", "<br>")
        if self.result['video_error']:
            vids_text += t.translate('video_error')

        # add HTML space after comma so that UI displays correctly
        self.analysis_docs.setText(docs_text.replace(", ", ",&nbsp;"))
        self.analysis_vids.setText(vids_text.replace(", ", ",&nbsp;"))

        if self.result['pdf_pages'] > 0 and self.result['video_seconds'] > 0:
            tot_text += t.translate('tot_text',
                                    t.human_readable_time(docs_time + vids_time)).replace("\n", "<br>")
            self.analysis_tot.setText(tot_text.replace(", ", ",&nbsp;"))

        prep_text = t.translate('prep_text',
                                t.get_hours(self.day_hours),
                                t.get_days(ceil((docs_time + vids_time) / 3600 / self.day_hours))).replace("\n", "<br>")
        self.analysis_prep.setText(prep_text.replace(", ", ",&nbsp;"))

    def click_directory_button(self):
        save_slider_preferences(self)
        show_file_dialog()


def save_slider_preferences(widget: ShowResult):
    set_preference(Preference.docs_seconds.value,
                   PreferenceDefault.docs_seconds.value,
                   widget.docs_seconds)
    set_preference(Preference.vids_multiplier.value,
                   PreferenceDefault.vids_multiplier.value,
                   widget.vids_multiplier)
    set_preference(Preference.day_hours.value,
                   PreferenceDefault.day_hours.value,
                   widget.day_hours)


def _set_fusion_dark_mode(enabled: bool):
    if enabled:
        app.setStyle('fusion')
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)
    else:
        app.setStyle(default_style)
        app.setPalette(default_palette)


def toggle_dark_mode():
    window.dark_mode_enabled = not window.dark_mode_enabled
    _set_fusion_dark_mode(window.dark_mode_enabled)


def main():
    global t
    t = Translator()
    global app
    app = QApplication(argv)
    global default_style
    default_style = str(app.style().objectName())
    global default_palette
    default_palette = app.palette()
    global window
    # global height
    window = Window()
    global width
    width = window.width()
    # height = window.height()
    sysexit(app.exec_())


if __name__ == "__main__":
    # redirect GTK warnings to logfile instead of the console
    if platform.startswith("linux"):
        Path.mkdir(DB_PATH, exist_ok=True)
        with redirect_stderr(open(str(Path.joinpath(DB_PATH, "errors_log.txt")), 'w')):
            main()
    else:
        main()
