import argparse

from lib.spreadsheet import Spreadsheet
from lib.spreadsheet import parser as spreadsheet_parser

parent_parsers = [spreadsheet_parser]
parser = argparse.ArgumentParser(description='Add YouTube metadata and publish new videos', parents=parent_parsers)

args = parser.parse_args()

spreadsheet = Spreadsheet(args.spreadsheet_id)
spreadsheet.get_youtube_talks()