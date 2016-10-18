import argparse
import requests


parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', add_help=False)
parser.add_argument('--schedule-path', dest='schedule_path', help='URL to schedule.json', default='https://raw.githubusercontent.com/pyconca/2016-web/master/web/data/schedule.json')
parser.add_argument('--talk-root', dest='talk_root', help='URL to the root directory for JSON talks', default='https://2016.pycon.ca/en/schedule/')


def get_slides(schedule_path, talk_root):
    response = requests.get(schedule_path)
    assert response.status_code == 200
    schedule = response.json()

    slides = []

    for day in schedule['days']:
        for entry in day['entries']:
            if 'talks' in entry.keys():
                for room, slug in entry['talks'].iteritems():
                    if slug:  # slug can be empty if there's not a talk scheduled at that time
                        response = requests.get(talk_root + slug + '.json')
                        assert response.status_code == 200
                        slide = {
                            'date': day['date'],
                            'room': room,
                            'slug': slug,
                            'talk': response.json()
                        }
                        slides.append(slide)
            elif 'keynote' in entry['title'].lower():
                # there is special handling for keynotes because they're not in the same format as other talks
                slug = 'keynote-' + entry['content'].lower().replace(' ', '-')  # for keynotes, entry['content'] is speaker's name
                slide = {
                    'date': day['date'],
                    'room': '1-067',
                    'slug': slug,
                    'talk': {
                        'title': [entry['title']],
                        'speakers': [entry['content']],
                        'start_time': [entry['start_time']],
                    }
                }

                slides.append(slide)

    return slides