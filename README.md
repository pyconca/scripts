# scripts

This repository will house various scripts that can be used from year-to-year.

## Installation

Install webkit2png

    $ brew install webkit2png

Clone the repo

    $ git checkout https://github.com/pyconca/scripts.git

Create a virtualenv

    $ mkvirtualenv -p `which python2.7` scripts && cd scripts

Install PIP requirements

    (scripts) $ pip install -r requirements.txt

## Slide Generation Script

The Slide Generation script takes certain JSON file with schedule and talk data, and creates PNG slides. The slides are
used as intros to the YouTube videos of PyCon talks.

### Running

Change directories to the root directory of this repo, and run:

    (scripts) $ python gen_slides/gen_slides.py ~/projects/2016-web/web/data/schedule.json

[schedule.json](https://github.com/pyconca/2016-web/blob/master/web/data/schedule.json) is a JSON file with the
schedule for PyCon Canada.

For more options run

    (scripts) $ python gen_slides/gen_slides.py --help