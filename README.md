YouTube Sync App
================

Retrieve YouTube videos and sync to the view.ly platform.

To run the app, you need to get the YouTube API client ID and secret as explained in the official [YouTube guide](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps). Note that when creating credentials, you need to set the `redirect_uri` to `http://localhost:5000/oauth2callback` After creating your credentials, download the `client_secrets.json` file and store it in the same dir with `app.py`.

Run the app:

    python youtube-sync/app.py
