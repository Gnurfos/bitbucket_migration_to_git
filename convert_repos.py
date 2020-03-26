#!/usr/bin/env python3

"""
Script migrating a user's bitbucket mercurial repositories to git
See README for more details
"""

import os
import http
import subprocess
import sys
import tempfile

import requests


user = '.....'
password = '....'
max_repos = 40
fast_export = os.path.expanduser('~/install/fast-export/hg-fast-export.sh')
# This will be used for manual cloning, and should be the same-ish version as will be called by fast-export
hg = '/usr/bin/hg'

auth = (user, password)


def main():
    if '-v' in sys.argv:
        http.client.HTTPConnection.debuglevel = 1

    repos = list_repos()
    print(f'{len(repos)} repos')

    mercurial_repos = [r for r in repos if r['scm'] == 'hg']

    print(f'{len(mercurial_repos)} hg repos')

    # repos_to_convert = [r for r in mercurial_repos if r['name'] == 'some_name']
    repos_to_convert = mercurial_repos
    for repo in repos_to_convert:
        convert(repo)


def list_repos():
    repo_list_url = f'https://bitbucket.org/!api/2.0/repositories/{user}?pagelen={max_repos}'
    response = requests.get(repo_list_url, auth=auth)
    repos = response.json()['values']
    return repos


def convert(repo):
    repo_name = repo['name']
    description = repo['description']
    language = repo['language']
    print(f'Converting {repo_name}')
    git_name = repo_name + '_git'
    git_slug = repo['slug'] + '_git'
    new_repo = create_repo(git_name, git_slug, description, language)
    convert_and_copy(repo, new_repo)


def create_repo(name, slug, description, language):
    repo_url = f'https://bitbucket.org/!api/2.0/repositories/{user}/{slug}'
    data = {
        'name': name,
        'scm': 'git',
        'description': description,
        'language': language,
        'is_private': True,
    }
    response = requests.post(repo_url, auth=auth, json=data)
    response.raise_for_status()
    print(f'Repo created: {name}')
    new_repo = response.json()
    return new_repo


def convert_and_copy(source_repo, target_repo):
    source_url = get_url(source_repo)
    target_url = get_url(target_repo)
    tempdir = tempfile.mkdtemp(suffix='_convert_repos')
    hg_dir = os.path.join(tempdir, 'hg')
    run(f'hg clone {source_url} {hg_dir}', cwd=tempdir)
    git_dir = os.path.join(tempdir, 'git')
    os.mkdir(git_dir)
    run(f'git init', cwd=git_dir)
    run(f'{fast_export} -r {hg_dir}', cwd=git_dir, env={'PYTHON': sys.executable})
    run(f'git push --all {target_url}', cwd=git_dir)
    run(f'git push --tags {target_url}', cwd=git_dir)


def run(command, *args, **kwargs):
    print(f'Running: {command}')
    subprocess.check_call(command, *args, shell=True, **kwargs)


def get_url(repo):
    for clone_method in repo['links']['clone']:
        if clone_method['name'] == 'ssh':
            return clone_method['href']
    raise RuntimeError(f'no SSH url found for {repo}')


if __name__ == '__main__':
    main()
