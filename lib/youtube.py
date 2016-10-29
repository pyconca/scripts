import httplib2
import os
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


CLIENT_SECRETS_FILE = 'client_secret.json'

YOUTUBE_SCOPE = 'https://www.googleapis.com/auth/youtube'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE)

home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
credential_path = os.path.join(credential_dir, 'youtube.googleapis.com-pyconca-video-production.json')

store = Storage(credential_path)

credentials = store.get()

if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, store, flags)

service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
video_response = service.videos().list(
    id='v4dXM35OWWE',
    part='contentDetails'
).execute()


class YouTubeStatus(object):

    PRIVATE = u'private'
    UNLISTED = u'unlisted'
    PUBLIC = u'public'


class YouTubeVideo(object):

    def __init__(self, youtube_id):
        self.youtube_id = youtube_id


class YouTube(object):

    def get_private_videos(self, ids):
        response = service.videos().list(
            id=','.join(ids),
            part='status'
        ).execute()

        items = response['items']
        items = filter(lambda item: item['status']['privacyStatus'] == YouTubeStatus.PRIVATE, items)

        return [YouTubeVideo(item['id']) for item in items]