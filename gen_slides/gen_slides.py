import argparse
import errno
import json
import os
import requests
import shutil
import subprocess

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data')
parser.add_argument('--schedule_path', help='URL to schedule.json', default='https://2016.pycon.ca/en/schedule/schedule.json')
parser.add_argument('--talk-root', dest='talk_root', help='URL to the root directory for JSON talks', default='https://2016.pycon.ca/en/schedule/')
parser.add_argument('--webkit2png-path', dest='webkit2png_path', help='Path for webkit2png executable', default='/usr/local/bin/webkit2png')
parser.add_argument('--height', dest='height', help='Height for the slides', default='768')
parser.add_argument('--width', dest='width', help='Width for the slides', default='1024')
parser.add_argument('--output-dir', dest='output_dir', help='Path to output directory', default='gen_slides/output')

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

    start_time = slide['talk']['start_time'][0].replace(':', '')  # it's no good to have ':' in a filename
    file_name = '{}_{}.html'.format(start_time, slide['slug'])
    html_path = os.path.join(html_room_dir, file_name)

    env = Environment(loader=FileSystemLoader('gen_slides/templates'))
    template = env.get_template('slide.html')
    html = template.render(slide=slide, BASE_DIR=os.getcwd() + '/gen_slides')
    html_file = open(html_path, 'wb')
    html_file.write(html.encode('utf8'))
    html_file.close()
    return html_path


def html_to_png(html_path):
    png_path = html_path.replace('/html/', '/png/') \
        .replace('.html', '')
    png_dir, png_name = os.path.split(png_path)

    fnull = open(os.devnull, 'w')
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
    ], stdout=fnull)
    return png_path + '-full.png'


def get_slides():
    response = requests.get(args.schedule_path)
    assert response.status_code == 200
    schedule = response.json()

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

base_dir = args.output_dir
html_dir = os.path.join(base_dir, 'html')

try:
    shutil.rmtree(base_dir)
except OSError as e:
    if e.errno == errno.ENOENT:  # no such file or directory
        pass
    else:
        raise

os.makedirs(html_dir)

print('Retrieving schedule and talk information')
slides = get_slides()
print('Generating HTML slides')
html_paths = map(generate_html, slides)
print('Converting HTML slides to PNGs')
png_paths = map(html_to_png, html_paths)
