import argparse
import os
from github import Github

service = Github(os.environ['PYCONCA_GITHUB_LOGIN_USERNAME'], os.environ['PYCONCA_GITHUB_LOGIN_PASSWORD'])

parser = argparse.ArgumentParser(description='GitHub API Wrapper', add_help=False)
parser.add_argument('--repo-user', default='pyconca', dest='repo_user', help='Username for the PyCon Canada GitHub account')
parser.add_argument('--repo', default='2016-web', help='Name of the website repo')


class Git(object):

    def __init__(self, user, repo):
        self.user = user
        self.repo = repo

    def add_youtube_to_talk(self, slug, youtube_id):
        user = service.get_user(self.user)
        repo = user.get_repo(self.repo)
        path = '/web/markdown/talks/{}_en.markdown'.format(slug)
        contents = repo.get_file_contents(path)

        # Add YouTube ID to content
        decoded_content = contents.decoded_content.split('\n')
        decoded_content = [line for line in decoded_content if 'youtube' not in line.lower()]
        i = -1
        for j in xrange(2):
            i = decoded_content.index('---', i + 1)
        decoded_content.insert(i, 'youtube: ' + youtube_id)
        decoded_content = '\n'.join(decoded_content)

        repo.update_file(path, 'Added YouTube ID for ' + slug, decoded_content, contents.sha)
