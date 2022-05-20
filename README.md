# Study Planner

[![Build and release](https://github.com/e-caste/study-planner/actions/workflows/build-release.yml/badge.svg)](https://github.com/e-caste/study-planner/actions/workflows/build-release.yml) [![Supported Python versions](https://img.shields.io/badge/python-3.6+-brightgreen?style=plastic&logo=python)]() [![GitHub license](https://img.shields.io/github/license/e-caste/study-planner?style=plastic&logo=gnu)](https://github.com/e-caste/study-planner/blob/master/LICENSE) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/e-caste/study-planner?color=lightblue&style=plastic)](https://github.com/e-caste/study-planner/releases) ![GitHub all releases](https://img.shields.io/github/downloads/e-caste/study-planner/total?color=%23FECF0E&style=plastic) [![Telegram channel and group](https://img.shields.io/badge/chat-on%20Telegram-blue?style=plastic&logo=telegram)](https://t.me/studyplannerupdates) 

A cross-platform GUI to get a quick analysis from files and/or directories in terms of required time to study their contents

<p align="center">
    <a href="https://github.com/e-caste/study-planner/releases">
        <img max-height="40" src="readme/download_button.png" alt="Download latest release">
    </a>
</p>

<hr />

<p align="center">
  <img max-height="150" src="readme/windows_screenshot.png" alt="Windows">
  <img max-height="400" src="readme/ubuntu_screenshot.png" alt="Ubuntu">
  <img max-height="500" src="readme/mac_screenshot.png" alt="macOS">
</p>

### How to run

1. Download the latest release for your platform on the right of this page or [click here](https://github.com/e-caste/study-planner/releases)
2. Decompress the archive
3. Run the application

Some notes on point 3:
- on Windows, you will have to click "More info" and then "Run anyway" in the blue window that appears the first time you run the app
- on macOS, you will have to double click the `RUNME.command` file before you can open the app
- on GNU/Linux, if you're using the Nautilus file manager (the default on Ubuntu), you will have to run the app from the terminal since double click does not work properly 

### How to develop
- `git clone https://github.com/e-caste/study-planner`
- `cd study-planner`
- `python3.9 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements-dev.txt`
- `python main.py`

On GNU/Linux you need to install `gcc`, `libxcb-xinerama0`, and `libmediainfo-dev` with your distribution's package manager.

### Credits

Icon by <a href="https://freeicons.io/profile/6156">Reda</a> on <a href="https://freeicons.io">freeicons.io</a>
                                
