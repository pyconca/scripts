import argparse
import string

import httplib2
import os

import re
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

parser = argparse.ArgumentParser(description='Google Sheets API Wrapper', add_help=False)
parser.add_argument('spreadsheet_id', help='Google Spreadsheet ID')

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-pyconca-video-production.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Video Production'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-pyconca-video-production.json')

    # create a dummy flags because otherwise we can't customize command line options
    flags = tools.argparser.parse_args({})

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags=flags)
        print('Storing credentials to ' + credential_path)
    return credentials

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
discovery_url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)


class Columns(object):
    """
    Column keys and names can be added here.
    """

    COLUMNS = [
        ('SLUG',                'Slug'),
        ('DAY',                 'Day'),
        ('TIME',                'Time'),
        ('ROOM',                'Room'),
        ('PRESENTATION_TITLE',  'Presentation Title'),
        ('DESCRIPTION',         'Description'),
        ('SPEAKER',             'Speaker'),
        ('YOUTUBE_URL',         'YouTube URL'),
        ('PUBLISHED_STATUS',    'Published Status'),
        ('NOTES',               'Notes'),
    ]

    KEYS = [column[0] for column in COLUMNS]

    NAMES = [column[1] for column in COLUMNS]

    NAME_TO_LETTER = dict([(column, ascii) for column, ascii in zip(KEYS, string.ascii_uppercase)])
    NAME_TO_NUMBER = dict([(column, number) for number, column in enumerate(KEYS)])


class SpreadsheetTalk(object):

    def __init__(self, spreadsheet, row, slug, date, start_time, room, title, description=None,
                 speakers=None, youtube_url=None, published_status=False):
        self.spreadsheet = spreadsheet
        self.row = row
        self.slug = slug
        self.date = date
        self.start_time = start_time
        self.room = room
        self.title = title
        self.description = description
        self.speakers = speakers
        self.youtube_url = youtube_url
        self._published_status = published_status

    @property
    def youtube_id(self):
        if not self.youtube_url:
            return None

        p = re.compile(r'\b[A-Za-z0-9_-]{11}\b')  # this should capture the ID from most or all YouTube URLs
        match = p.findall(self.youtube_url)
        print(self.speakers)
        assert len(match) == 1, 'Zero or more than one YouTube IDs found in {}'.format(self.youtube_url)
        return match[0]

    @property
    def published_status(self):
        return self._published_status

    @published_status.setter
    def published_status(self, value):
        range = Columns.NAME_TO_LETTER['PUBLISHED_STATUS'] + str(self.row)

        body = {
            'values': [[str(value)]]
        }

        service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet.spreadsheet_id, range=range, body=body, valueInputOption='RAW'
        ).execute()
        self._published_status = value


class Spreadsheet(object):

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def create_header(self):
        """Creates and formats the header of the spreadsheet"""

        body = {
            'values': [
                Columns.NAMES
            ]
        }

        service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range='A1', valueInputOption='RAW', body=body
        ).execute()

        requests = []

        # Turn header into a 'frozen' row that always stays at the top of the sheet when scrolling
        requests.append({
            'updateSheetProperties': {
                'properties': {
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                },
                'fields': 'gridProperties.frozenRowCount'
            }
        })

        # Format header
        requests.append({
            'repeatCell': {
                'range': {
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 1.0,
                            'green': 1.0,
                            'blue': 1.0
                        },
                        'horizontalAlignment': 'CENTER',
                        'textFormat': {
                            'foregroundColor': {
                                'red': 0.18,
                                'green': 0.48,
                                'blue': 0.83
                            },
                            'fontSize': 12,
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        })

        service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                           body={'requests': requests}).execute()

    def add_conditional_formatting(self):
        requests = []

        # Make "Uploaded to YouTube" column values green if equal to 'Yes'
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'startColumnIndex': Columns.NAME_TO_NUMBER['YOUTUBE_URL'],
                            'endColumnIndex': Columns.NAME_TO_NUMBER['YOUTUBE_URL'] + 1,
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'NOT_BLANK'
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 0.18,
                                'green': 0.83,
                                'blue': 0.43,
                            }
                        }
                    }
                },
                'index': 0
            }
        })

        # Make "Uploaded to YouTube" column values red if equal to anything but 'Yes'
        requests.append({
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [
                        {
                            'sheetId': 0,
                            'startRowIndex': 1,
                            'startColumnIndex': Columns.NAME_TO_NUMBER['YOUTUBE_URL'],
                            'endColumnIndex': Columns.NAME_TO_NUMBER['YOUTUBE_URL'] + 1,
                        }
                    ],
                    'booleanRule': {
                        'condition': {
                            'type': 'BLANK'
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 0.83,
                                'green': 0.18,
                                'blue': 0.18,
                            }
                        }
                    }
                },
                'index': 1
            }
        })

        service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                body={'requests': requests}).execute()

    def add_talks(self, talks):
        """Takes Talks and adds them to the spreadsheet. Will overwrite any existing data"""

        values = [
            [
                talk.slug,
                talk.date,
                talk.start_time,
                talk.room,
                talk.title,
                talk.description,
                talk.speakers,
            ]
            for talk in talks
        ]

        body = {
            'values': values
        }

        service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range='A2', valueInputOption='RAW', body=body
        ).execute()

    def get_unpublished_youtube_talks(self):
        """
        Find unpublished talks that have YouTube IDs. This means they're ready to be published.
        """

        range = 'A2:{}'.format(Columns.NAME_TO_LETTER['PUBLISHED_STATUS'])

        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range
        ).execute()
        rows = result.get('values', [])

        def is_unpublished(talk):
            if talk.youtube_id:
                if not talk.published_status or talk.published_status.lower() != 'true':
                    return True
            return False

        def clean_value(value):
            if value:
                value = value.strip()
            if not value:
                return None
            return value

        talks = []
        for row in rows:
            # Pad values to match total number of columns
            row += [None] * (len(Columns.KEYS) - len(row))

            # Strip whitespace and replace empty values with None
            row = [clean_value(value) for value in row]
            talks.append(SpreadsheetTalk(self, *row))

        unpublished_talks = filter(is_unpublished, talks)
        return unpublished_talks