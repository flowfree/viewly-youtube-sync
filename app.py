#!/usr/bin/env python
# encoding: utf-8

import json

from flask import (
    Flask, request, session, url_for, redirect,
)
from apiclient import discovery
from oauth2client import client
import httplib2


app = Flask(__name__)


@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        youtube = discovery.build('youtube', 'v3', http_auth)
        channel = youtube.channels().list(mine=True, part='snippet').execute()
        return json.dumps(channel)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/youtube.force-ssl',
        redirect_uri=url_for('oauth2callback', _external=True),
    )
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)  
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        return redirect(url_for('index'))


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug = True
    app.run(port=3000)
