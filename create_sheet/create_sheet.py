import argparse

from lib.spreadsheet import Spreadsheet
from lib.talks import get_talks
from lib.talks import parser as talks_parser

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', parents=[talks_parser])

args = parser.parse_args()


spreadsheet = Spreadsheet('1bGHyPdeUy1QCMQdHzNgtY3KBJoqrVxWu32DuusczC88')
spreadsheet.create_header()
talks = get_talks(args.schedule_path, args.talk_root)
spreadsheet.add_talks(talks)