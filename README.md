# Study Planner

[![Supported Python versions](https://img.shields.io/badge/python-3.6-brightgreen?style=plastic)]() [![GitHub license](https://img.shields.io/github/license/e-caste/study-planner?style=plastic)](https://github.com/e-caste/study-planner/blob/master/LICENSE)    

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/e-caste/study-planner?style=social)](https://github.com/e-caste/study-planner/releases) 

A cross-platform GUI to get a quick analysis from files and/or directories in terms of required time to study their contents

<p align="center">
  <img height="150" src="readme/windows_screenshot.png" alt="Windows">
  <img height="400" src="readme/ubuntu_screenshot.png" alt="Ubuntu">
  <img height="500" src="readme/mac_screeshot.png" alt="macOS">
</p>

### How to run

1. Download the latest release for your platform on the right of this page
2. Decompress the archive
3. Run the application

Some notes on point 3:
- on Windows, you will have to click "More info" and then "Run anyway" in the blue window that appears the first time you run the app
- on macOS, you will have to double click the app while holding control, only then you will have the option to "Open" the app
- on GNU/Linux, if you're using the Nautilus file manager (the default on Ubuntu), you will have to run the app from the terminal since double click does not work properly 

### How to develop
- `git clone https://github.com/e-caste/study-planner`
- `cd study-planner`
- `python3.6 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements-dev.txt`
- `python main.py`
