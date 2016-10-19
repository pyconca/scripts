import argparse
from operator import itemgetter

from lib.spreadsheet import Spreadsheet
from lib.talks import get_talks
from lib.talks import parser as talks_parser

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', parents=[talks_parser])
parser.add_argument('spreadsheet_id', help='Google Spreadsheet ID')

args = parser.parse_args()


spreadsheet = Spreadsheet(args.spreadsheet_id)
print('Creating spreadsheet header')
spreadsheet.create_header()
print('Getting talks')
talks = get_talks(args.schedule_path, args.talk_root)
sorted(talks, key=itemgetter('date', 'start_time', 'room'))
print('Adding talks to spreadsheet')
spreadsheet.add_talks(talks)
print('Spreadsheet populated!')
print('URL: https://docs.google.com/spreadsheets/d/' + spreadsheet.spreadsheet_id)