# scripts

This repository will house various scripts that can be used from year-to-year.

## Installation

Clone the repo

    $ git clone https://github.com/pyconca/scripts.git

Create a virtualenv

    $ mkvirtualenv -p `which python2.7` scripts && cd scripts

Install PIP requirements

    (scripts) $ pip install -r requirements.txt

If running a script that uses the Google Sheets video production spreadsheet or
the YouTube API, create credentials using these
[instructions](https://developers.google.com/sheets/quickstart/python) and put
the credentials in `scripts/client_secret.json`

## Scripts

### Slide Generation Script

The Slide Generation script pulls JSONs from the web API that have schedule and talk data,
and creates PNG slides. The slides are used as intros to the YouTube videos of
PyCon talks.

#### Installation

Install webkit2png

    $ brew install webkit2png

#### Running

Change directories to the root directory of this repo, and run:

    (scripts) $ PYTHONPATH=. python create_slides/create_slides.py

The slides will be in `create_slides/output`.

For more options run

    (scripts) $ PYTHONPATH=. python create_slides/create_slides.py --help

### Video Upload Spreadsheet Creation Script

The Spreadsheet Creation script populates a Google Sheets spreadsheet with
information about all of the PyCon Canada talks. The spreadsheet can be provided
to the company that does video production, and they can use it to track which
videos have been uploaded to YouTube.

#### Installation

Follow the instructions at https://developers.google.com/sheets/quickstart/python,
and then put the client secret file in `client_secret_sheets.json`.

#### Running

You must first create a spreadsheet in the shared PyCon Canada Google Drive,
then copy the spreadsheet's ID from the URL.

You can get

    (scripts) $ PYTHONPATH=. python populate_sheet/populate_sheet.py [SPREADSHEET_ID]

### Publish Videos Script

This script finds newly uploaded YouTube videos based on the Google Sheets
spreadsheet, and then sets certain metadata (like title, category, and
description). It also sets the video to 'Delisted' status, which means it will
be available to anyone who has a link.

#### Running

    (scripts) $ PYTHONPATH=. python publish_videos/publish_videos.py [SPREADSHEET_ID]
