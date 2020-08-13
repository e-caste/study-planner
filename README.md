# study-planner
[![Supported Python versions](https://img.shields.io/badge/python-3.6-brightgreen)]() [![GitHub license](https://img.shields.io/github/license/e-caste/study-planner)](https://github.com/e-caste/study-planner/blob/master/LICENSE) [![version](https://img.shields.io/badge/version-1.0-orange)]()    
A CLI tool to get a quick analysis from in terms of required time to study its content

### Example usage

`python main.py /path/to/an/exam/directory/`                 
```
There are 1250 pdf pages to study in the given directories spanning 41 files.
At 1 minute per page, it will take you 20 hour(s) and 50 minute(s) to study these documents.
At 2 minutes per page, it will take you 41 hour(s) and 40 minute(s) to study these documents.
Instead, skimming very quickly (20 seconds per page) will take you 6 hour(s) and 56 minute(s).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are 32 hour(s) and 16 minute(s) to watch in the given directories divided between 44 videos.
At 1.5x it will take you 21 hour(s) and 30 minute(s) to finish.
At 2x it will take you 16 hour(s) and 8 minute(s).
Instead, accounting for pauses to take notes (0.75x), it will take you 43 hour(s) and 1 minute(s).
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In total, it will take you approximately 73 hour(s) and 56 minute(s) to study everything in the given directories.
Going very fast (20 seconds per page, watching videos at 2x) will take you 23 hour(s) and 4 minute(s).
Taking your time to master the subject (2 minutes per page, watching videos at 0.75x) will take you 84 hour(s) and 41 minute(s).
```

### How to install
- `git clone https://github.com/e-caste/study-planner`
- `cd study-planner`
- `python3.8 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
