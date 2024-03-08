# SPDX-FileCopyrightText: 2024 PeARS Project, <community@pearsproject.org>, 
#
# SPDX-License-Identifier: AGPL-3.0-only

import click
from shutil import copy2, copytree
from os.path import dirname, realpath, join, isfile
from datetime import datetime
from pathlib import Path
from flask import Blueprint
from app.indexer.controllers import run_indexer_url
from app.indexer.access import request_url
from app.indexer.htmlparser import extract_links
from app import db, User, Urls

pears = Blueprint('pears', __name__)

@pears.cli.command('setadmin')
@click.argument('username')
def set_admin(username):
    '''Use from CLI with flask pears setadmin <username>.'''
    user = User.query.filter_by(username=username).first()
    user.is_admin = True
    db.session.commit()
    print(username,"is now admin.")


@pears.cli.command('index')
@click.argument('contributor')
@click.argument('path')
def index(contributor, filepath):
    '''
    Index from a manual created URL file.
    The file should have the following information,
    separated by semi-colons:
    url; theme; trigger; contributor
    with one url per line.
    Use from CLI with flask pears index <contributor> <path>
    '''
    run_indexer_url(contributor, filepath) 


@pears.cli.command('getlinks')
@click.argument('url')
def get_links(url):
    '''Get links from a particular URL'''
    access, req, request_errors = request_url(url)
    if access:
        links = extract_links(url)
        for link in links:
            print(link)
    else:
        print("Access denied.")


@pears.cli.command('exporturls')
def export_urls():
    '''Get all URLs on this instance'''
    urls = Urls.query.all()
    for u in urls:
        theme = u.pod.split('.u.')[0]
        print(u.url+';'+theme+';'+u.trigger+';'+u.contributor)

@pears.cli.command('backup')
@click.argument('backupdir')
def backup(backupdir):
    '''Backup database and pods to specified directory'''
    dir_path = dirname(dirname(dirname(realpath(__file__))))
    pod_dir = join(dir_path,'app','static','pods')
    #Check if directory exists, otherwise create it
    Path(backupdir).mkdir(parents=True, exist_ok=True)
    #Get today's date
    date = datetime.now().strftime('%Y-%m-%d-%Hh%Mm')
    dirpath = join(backupdir,'pears-'+date)
    Path(dirpath).mkdir(parents=True, exist_ok=True)
    #Copy database
    copy2('app.db',dirpath)
    #Copy pods folder
    copytree(pod_dir, join(dirpath,'pods'))