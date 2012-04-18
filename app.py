import os

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

###########################################################################
from radiowut import (user_key_for_username, artists_in_user_collection,
    get_new_releases)

@app.route('/<username>/')
def userview(username):
    view_cachekey = "userview(username=%s)" % username
    output = cache_get(u_cachekey)
    if not output:
        user_key = user_key_for_username(username)
        if user_key == 0:
            return "Unknown user"

        try:
            artist_key_set = artists_in_user_collection(user_key)
        except:
            artist_key_set = []

        new_releases = get_new_releases()

        user_new_releases = filter(
            lambda release: release.get("artistKey", "").split("|", 1)[0] in artist_key_set,
            new_releases
        )
        output = """<p>New releases (past two weeks) for artists in <b>%s</b>'s collection:</p><hr>""" % (
            username
        )
        for release in user_new_releases:
            output += """
            <div style="width:220px;height:300px;text-align:center;padding:10px;margin:10px;float:left;overflow-y:auto">
                <a href="%s"><img src="%s" alt="%s album cover"/></a><br>
                <a href="%s"><b>%s</b></a><br>
                <a href="http://rdio.com/#%s"><i>%s</i></a><br>
                Released %s
            </div>""" % (
                release['embedUrl'],
                release['icon'],
                release['name'],
                release['embedUrl'],
                release['name'],
                release['artistUrl'],
                release['artist'],
                release['displayDate']
            )
        cache_set(view_cachekey, output, 1800)

    return output

###########################################################################

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
