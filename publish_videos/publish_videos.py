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
talks = spreadsheet.get_youtube_talks()
ids = [talk.youtube_id for talk in talks]
print('Getting private videos from YouTube')
private_videos = youtube.get_private_videos(ids)
print('{} private videos found on YouTube'.format(len(private_videos)))

for private_video in private_videos:
    talk = filter(lambda x: x.youtube_id == private_video.youtube_id, talks)[0]
    print('Unpublished talk: {}'.format(talk.title))
    print('\tYouTube ID: {}'.format(private_video.youtube_id))
    print('\tSetting metadata and setting status to UNLISTED')
    private_video.publish(talk.title, talk.description)
    print('\tUpdating spreadsheet to set published status to true')
    talk.published_status = True