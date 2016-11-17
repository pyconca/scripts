import argparse

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', add_help=False)
parser.add_argument('--schedule-path', dest='schedule_path', help='URL to schedule.json', default='https://raw.githubusercontent.com/pyconca/2016-web/master/web/data/schedule.json')
parser.add_argument('--talk-root', dest='talk_root', help='URL to the root directory for JSON talks', default='https://2016.pycon.ca/en/schedule/')


class Talk(object):

    def __init__(self, room, slug, date, title, description, start_time, speakers):
        self.room           = room
        self.slug           = slug
        self.date           = date
        self.title          = title
        self.description    = description
        self.start_time     = start_time
        self.speakers       = speakers


def get_talks(schedule_path, talk_root):
    response = requests.get(schedule_path)
    assert response.status_code == 200
    schedule = response.json()

    talks = []

    for day in schedule['days']:
        for entry in day['entries']:
            if 'talks' in entry.keys():
                for room, slug in entry['talks'].iteritems():
                    if slug and not room == 'tutorial':  # Filter out tutorials, and no slug (which means there's no talk scheduled)
                        response = requests.get(talk_root + slug + '.json')
                        assert response.status_code == 200

                        response_json = response.json()
                        description = BeautifulSoup(response_json['description'], 'html.parser').get_text()
                        description = description.split('Bio')[0]
                        description = description.rsplit('\n', 1)[0]

                        talk = Talk(**{
                            'date': response_json.get('date'),
                            'room': room,
                            'slug': slug,
                            'title': response_json.get('title'),
                            'speakers': response_json.get('speakers'),
                            'start_time': response_json.get('start_time'),
                            'description': description
                        })
                        talks.append(talk)

            elif 'keynote' in entry['title'].lower():
                # there is special handling for keynotes because they're not in the same format as other talks

                response_json = Talk(**{
                    'date': day['date'],
                    'room': '1-067',
                    'slug': entry['link'],
                    'title': entry['title'],
                    'speakers': entry['content'],
                    'start_time': entry['start_time'],
                    'description': ''   # keynotes do not have descriptions
                })
                talks.append(response_json)

    return talks
