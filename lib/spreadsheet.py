import argparse

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', add_help=False)
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


class SpreadsheetTalk(object):

    def __init__(self, slug, date, start_time, room, title, speakers, youtube_id=None):
        self.slug = slug
        self.date = date
        self.start_time = start_time
        self.room = room
        self.title = title
        self.speakers = speakers


class Spreadsheet(object):

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def create_header(self):
        """Creates and formats the header of the spreadsheet"""

        body = {
            'values': [
                [
                    'Slug', 'Day', 'Time', 'Room', 'Presentation Title', 'Speaker', 'YouTube ID',
                    'YouTube Status', 'Notes'
                ]
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
                            'startColumnIndex': 6,
                            'endColumnIndex': 7,
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
                            'startColumnIndex': 6,
                            'endColumnIndex': 7,
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
                talk['slug'],
                talk['date'],
                talk['start_time'],
                talk['room'],
                talk['title'],
                talk['speakers'],
            ]
            for talk in talks
        ]
        body = {
            'values': values
        }

        service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range='A2', valueInputOption='RAW', body=body
        ).execute()

    def get_youtube_talks(self):
        result = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range='A2:G'
        ).execute()
        values = result.get('values', [])

        # There must be a value in the 7th column to check if there is a YouTube ID
        values = filter(lambda x: len(x) >= 7 and x[6].strip(), values)
        return [SpreadsheetTalk(*value) for value in values]