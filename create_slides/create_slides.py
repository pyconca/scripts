import argparse
import errno
import os
import shutil
import subprocess

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader

from lib.talks import get_talks
from lib.talks import parser as slides_parser

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data', parents=[slides_parser])
parser.add_argument('--webkit2png-path', dest='webkit2png_path', help='Path for webkit2png executable', default='/usr/local/bin/webkit2png')
parser.add_argument('--height', dest='height', help='Height for the slides', default='768')
parser.add_argument('--width', dest='width', help='Width for the slides', default='1024')
parser.add_argument('--output-dir', dest='output_dir', help='Path to output directory', default='create_slides/output')

args = parser.parse_args()


def generate_html(talk):
    html_room_dir = os.path.join(html_dir, talk['room'], str(talk['date']))

    try:
        os.makedirs(html_room_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    start_time = talk['start_time'][0].replace(':', '')  # it's no good to have ':' in a filename
    file_name = '{}_{}.html'.format(start_time, talk['slug'])
    html_path = os.path.join(html_room_dir, file_name)

    env = Environment(loader=FileSystemLoader('create_slides/templates'))
    template = env.get_template('slide.html')
    html = template.render(talk=talk, BASE_DIR=os.getcwd() + '/create_slides')
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
talks = get_talks(args.schedule_path, args.talk_root)
print('Generating HTML slides')
html_paths = map(generate_html, talks)
print('Converting HTML slides to PNGs')
png_paths = map(html_to_png, html_paths)
