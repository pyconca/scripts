import argparse

from lib.spreadsheet import Spreadsheet
from lib.spreadsheet import parser as spreadsheet_parser
from lib.youtube import YouTube

parent_parsers = [spreadsheet_parser]
parser = argparse.ArgumentParser(description='Add YouTube metadata and publish new videos', parents=parent_parsers)

args = parser.parse_args()

spreadsheet = Spreadsheet(args.spreadsheet_id)
youtube = YouTube()

print('Getting all talks from spreadsheet with YouTube IDs')
talks = spreadsheet.get_unpublished_youtube_talks()
print('{} unpublished talks'.format(len(talks)))
ids = [talk.youtube_id for talk in talks]
print('Getting videos from YouTube')
videos = youtube.get_videos(ids)

for talk in talks:
    print('Unpublished talk: {}'.format(talk.title))
    video = filter(lambda x: talk.youtube_id == x.youtube_id, videos)[0]
    print('\tYouTube ID: {}'.format(video.youtube_id))
    print('\tSetting metadata and setting status to UNLISTED')
    video.publish(talk.title, talk.description)
    print('\tUpdating spreadsheet to set published status to true')
    talk.published_status = True