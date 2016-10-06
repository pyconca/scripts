import argparse
import json
import os
import requests
from uuid import uuid4

parser = argparse.ArgumentParser(description='Generate YouTube video slides from JSON data')
parser.add_argument('schedule_path', help='Path to schedule.json')
parser.add_argument('--talk-root', dest='talk_root', help='URL to the root directory for JSON talks', default='https://2016.pycon.ca/en/schedule/')

args = parser.parse_args()
# def generate_html(slide):
#     html_room_dir = os.path.join(html_dir, slide['room'].name, str(slide['day'].date))
#     try:
#         os.makedirs(html_room_dir)
#     except FileExistsError:
#         pass
#     file_name = '{}_{}.html'.format(slide['next_start'].strftime('%H%M%S'), slide['slug'])
#     html_path = os.path.join(html_room_dir, file_name)
#     html = loader.render_to_string('slides/slide.html', slide)
#     html_file = open(html_path, 'wb')
#     html_file.write(html.encode('utf8'))
#     html_file.close()
#     html_paths.append(html_path)
#
#
# def html_to_png(html_path):
#     png_path = html_path.replace('/html/', '/png/') \
#         .replace('.html', '')
#     png_dir, png_name = os.path.split(png_path)
#     subprocess.check_call([
#         settings.WEBKIT2PNG_PATH,
#         '-F',  # just full size image
#         '-W',
#         str(settings.SLIDE_WIDTH),
#         '-H',
#         str(settings.SLIDE_HEIGHT),
#         '-D',
#         png_dir,
#         '-o',
#         png_name,
#         html_path,
#     ])
#     return png_path + '-full.png'
#
#


def get_slides():
    with open(args.schedule_path) as schedule_file:
        schedule = json.load(schedule_file)

    slides = []

    for day in schedule['days']:
        for entry in day['entries']:
            if 'talks' in entry.keys():
                for room, talk in entry['talks'].iteritems():
                    if talk:
                        response = requests.get(args.talk_root + talk + '.json')
                        assert response.status_code == 200
                        slide = {
                            'date': day['date'],
                            'room': room,
                            'talk': response.json()
                        }
                        slides.append(slide)

    return slides

base_dir = '/tmp/slides.' + uuid4().hex
html_dir = os.path.join(base_dir, 'html')

# try:
os.makedirs(html_dir)
html_paths = []

slides = get_slides()
print(slides)
# slides = Slides(days, talks)
# print(talk_jsons)
    # for slide in Slides():
    #     generate_html(slide)
#
#     png_paths = []
#     for html_path in html_paths:
#         png_paths.append(html_to_png(html_path))
#     print(png_paths)
#
#     zip_path = os.path.join(settings.MEDIA_ROOT, 'slides.zip')
#     zip = zipfile.ZipFile(zip_path, 'w')
#     for path in png_paths:
#         rel_path = '/'.join(path.split('/')[-3:])
#         zip.write(path, rel_path)
# finally:
#     shutil.rmtree(base_dir)