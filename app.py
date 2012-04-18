import os

from flask import Flask, request, redirect, url_for, escape
app = Flask(__name__)

@app.route('/')
def index():
    username = request.args.get('username', '')
    if username:
        username = escape(username[:100].replace(" ","-").lower().strip())
        return redirect(
            url_for('userview', username=username),
        )

    return """
        <h1>What's new for my Rdio collection?</h1>
        <form action="" method="get">
        Rdio Username: <input type="text" name="username" placeholder="my-rdio-username"/><br>
        <input type="submit" value="Submit"/>
        </form>
        <p><a href="https://github.com/mtigas/radiowut">this project is on github</a></p>
    """

###########################################################################
from cacheutil import cache_get, cache_set
from radiowut import (user_key_for_username, artists_in_user_collection,
    get_new_releases)

@app.route('/<username>/')
def userview(username):
    new_username = username[:100].lower().strip()
    if username != new_username:
        return redirect(
            url_for('userview', username=new_username),
        )

    view_cachekey = "userview1(username=%s)" % username
    output = cache_get(view_cachekey)
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
        output = """<p>New releases (past two weeks) for artists in <b><a href="http://rdio.com/people/%s">%s</a></b>'s <a href="http://rdio.com/people/%s/collection/">collection</a>:</p><hr>""" % (
            escape(username),
            escape(username),
            escape(username)
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
        output += """<br style="clear:both"><hr><p><a href="https://github.com/mtigas/radiowut">this project is on github</a></p>"""
        cache_set(view_cachekey, output, 21600)

    return output

###########################################################################

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
