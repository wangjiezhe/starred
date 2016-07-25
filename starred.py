#!/usr/bin/env python

import sys
from io import BytesIO
from collections import OrderedDict
import click
from github3 import GitHub


desc = '''# Starred


- [Content](#starred)

'''


html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)


@click.command()
@click.option('--username', envvar='USER', help='GitHub username')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub token')
@click.option('--sort',  is_flag=True, help='sort by language')
@click.option('--repository', default='', help='repository name')
def starred(username, token, sort, repository):
    """GitHub starred

    make your own awesome lists page by GitHub star!

    example:
        starred --username maguowei --sort > README.md
    """
    if repository:
        if not token:
            click.secho('Error: create repository need set --token', fg='red')
            return
        file = BytesIO()
        sys.stdout = file
    else:
        file = None

    gh = GitHub(token=token)
    stars = gh.starred_by(username)
    click.echo(desc)
    repo_dict = {}

    for s in stars:
        language = s.language or 'Others'
        description = html_escape(s.description).replace('\n', '') if s.description else ''

        if language not in repo_dict:
            repo_dict[language] = []

        repo_dict[language].append([s.name, s.html_url, description.strip()])

    if sort:
        repo_dict = OrderedDict(sorted(repo_dict.items(), key=lambda l: l[0]))

    for language in repo_dict.keys():
        data = u'    - [{}](#{})'.format(language, language.lower())
        click.echo(data)
    click.echo('')

    for language in repo_dict:
        click.echo('## %s\n' % language)
        for repo in repo_dict[language]:
            data = u'* [{}]({}) - {}'.format(*repo)
            click.echo(data)
        click.echo('')

    if file:
        rep = gh.repository(username, repository)
        if rep:
            readme = rep.readme()
            readme.update('update', file.getvalue())
        else:
            rep = gh.create_repository(repository, 'generated by starred')
            rep.create_file('README.md', 'starred initial commit', file.getvalue())
        click.launch(rep.html_url)

if __name__ == '__main__':
    starred()
