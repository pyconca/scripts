import argparse
import json
import os
import errno
import requests
from uuid import uuid4

import subprocess
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data')
parser.add_argument('schedule_path', help='Path to schedule.json')
parser.add_argument('--talk-root', dest='talk_root', help='URL to the root directory for JSON talks', default='https://2016.pycon.ca/en/schedule/')
parser.add_argument('--webkit2png-path', dest='webkit2png_path', help='Path for webkit2png executable', default='/usr/local/bin/webkit2png')
parser.add_argument('--height', dest='height', help='Height for the slides', default='768')
parser.add_argument('--width', dest='width', help='Width for the slides', default='1024')

args = parser.parse_args()


def generate_html(slide):
        html_room_dir = os.path.join(html_dir, slide['room'], str(slide['date']))
        try:
            os.makedirs(html_room_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        file_name = '{}_{}.html'.format(slide['talk']['start_time'][0], slide['slug'])
        html_path = os.path.join(html_room_dir, file_name)

        env = Environment(loader=PackageLoader('gen_slides', 'templates'))
        template = env.get_template('slide.html')
        html = template.render(slide=slide)
        html_file = open(html_path, 'wb')
        html_file.write(html.encode('utf8'))
        html_file.close()
        return html_path


def html_to_png(html_path):
    png_path = html_path.replace('/html/', '/png/') \
        .replace('.html', '')
    png_dir, png_name = os.path.split(png_path)
    subprocess.check_call([
        args.webkit2png_path,
        '-F',  # just full size image
        '-W',
        args.width,
        '-H',
        args.height,
        '-D',
        png_dir,
        '-o',
        png_name,
        html_path,
    ])
    return png_path + '-full.png'


def get_slides():
    with open(args.schedule_path) as schedule_file:
        schedule = json.load(schedule_file)

    slides = []

    for day in schedule['days']:
        for entry in day['entries']:
            if 'talks' in entry.keys():
                for room, slug in entry['talks'].iteritems():
                    if slug:  # slug can be empty if there's not a talk scheduled at that time
                        response = requests.get(args.talk_root + slug + '.json')
                        assert response.status_code == 200
                        slide = {
                            'date': day['date'],
                            'room': room,
                            'talk': response.json(),
                            'slug': slug
                        }
                        slides.append(slide)

    return slides

base_dir = '/tmp/slides.' + uuid4().hex
html_dir = os.path.join(base_dir, 'html')

os.makedirs(html_dir)

slides = get_slides()
html_paths = map(generate_html, slides)
png_paths = map(html_to_png, html_paths)
