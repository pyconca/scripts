# scripts

This repository will house various scripts that can be used from year-to-year.

## Installation

Clone the repo

    $ git clone https://github.com/pyconca/scripts.git

Create a virtualenv

    $ mkvirtualenv -p `which python2.7` scripts && cd scripts

Install PIP requirements

    (scripts) $ pip install -r requirements.txt

## Slide Generation Script

The Slide Generation script takes certain JSON file with schedule and talk data, and creates PNG slides. The slides are
used as intros to the YouTube videos of PyCon talks.

### Installation

Install webkit2png

    $ brew install webkit2png

### Running

Change directories to the root directory of this repo, and run:

    (scripts) $ python gen_slides/gen_slides.py

The slides will be in `gen_slides/output`.

For more options run

    (scripts) $ python gen_slides/gen_slides.py --help
