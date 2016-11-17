import argparse
from operator import attrgetter

from lib.spreadsheet import Spreadsheet
from lib.spreadsheet import parser as spreadsheet_parser
from lib.talks import get_talks
from lib.talks import parser as talks_parser

parent_parsers = [talks_parser, spreadsheet_parser]
parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', parents=parent_parsers)

args = parser.parse_args()

spreadsheet = Spreadsheet(args.spreadsheet_id)
print('Creating spreadsheet header')
spreadsheet.create_header()
print('Adding conditional formatting')
spreadsheet.add_conditional_formatting()
print('Getting talks')
talks = get_talks(args.schedule_path, args.talk_root)
sorted(talks, key=attrgetter('date', 'start_time', 'room'))
print('Adding talks to spreadsheet')
spreadsheet.add_talks(talks)
print('Spreadsheet populated!')
print('URL: https://docs.google.com/spreadsheets/d/' + spreadsheet.spreadsheet_id)