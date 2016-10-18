import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

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

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class Spreadsheet(object):

    def __init__(self, spreadsheet_id):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
        service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)

        self.service = service
        self.spreadsheet_id = spreadsheet_id

    def create_header(self):
        """Creates and formats the header of the spreadsheet"""

        body = {
            'values': [
                [
                    'Slug', 'Day', 'Time', 'Room', 'Presentation Title', 'Speaker', 'YouTube Name',
                    'Video Uploaded to YouTube', 'YouTube URL', 'YouTube Status', 'Notes'
                ]
            ]
        }

        self.service.spreadsheets().values().update(
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

        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                           body={'requests': requests}).execute()

    def add_talks(self, talks):
        """Takes talks and adds them to the spreadsheet. Will overwrite any existing data"""

        values = [
            [
                talk['slug'],                   # Slug
                talk['date'],                   # Date
                talk['start_time'][0],          # Time
                talk['room'],                   # Room
                talk['title'][0],               # Title
                talk['speakers'][0],            # Speakers
                '',                             # YouTube Name
                'No',                           # Uploaded to YouTube?
            ]
            for talk in talks
        ]
        body = {
            'values': values
        }

        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range='A2', valueInputOption='RAW', body=body
        ).execute()