#!/usr/bin/env python
# encoding: utf-8

import uuid
import json
import os
import sys

import httplib2
import dateutil.parser
from apiclient import discovery
from oauth2client import client
from flask import (
    Flask, request, session, url_for, redirect, jsonify, render_template
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, 'client_secrets.json')

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_list')
def video_list():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    http_auth = credentials.authorize(httplib2.Http())
    youtube = discovery.build('youtube', 'v3', http_auth)
    channel = youtube.channels().list(mine=True, part='contentDetails').execute()
    try:
        playlist_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except KeyError:
        return 'No uploaded videos.'
    data = youtube.playlistItems().list(
        playlistId=playlist_id, 
        maxResults=25, 
        part='snippet,contentDetails',
    ).execute()

    try:
        videos = data['items']
    except Exception as e:
        print(e)
        videos = []
    return render_template('video_list.html', videos=videos)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_JSON,
        scope='https://www.googleapis.com/auth/youtube.readonly',
        redirect_uri=url_for('oauth2callback', _external=True),
    )
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)  
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        return redirect(url_for('video_list'))


@app.route('/revoke')
def revoke():
    if 'credentials' in session:
        credentials = client.OAuth2Credentials.from_json(session['credentials'])
        credentials.revoke(httplib2.Http())
        return 'access revoked.'
    else:
        return 'no credentials in session'


@app.template_filter('datetime')
def datetime(s):
    dt = dateutil.parser.parse(s)
    return dt.strftime('%B %d, %Y')


if __name__ == "__main__":
    if not os.path.isfile(CLIENT_SECRETS_JSON):
        print('Please obtain the Youtube API client ID and secret.')
        sys.exit()
    app.secret_key = str(uuid.uuid4())
    app.debug = not bool(os.getenv('PRODUCTION'))
    app.run(host=os.getenv('FLASK_HOST', '127.0.0.1'), port=5000)
