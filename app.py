import os
from flask import Flask, request, redirect, url_for, escape, render_template
from cacheutil import cache_get, cache_set
from radiowut import (user_key_for_username, artists_in_user_collection,
    get_new_releases)


app = Flask(__name__)

def google_analytics_id():
    return os.environ.get('GA_ANALYTICS_ID', None)

###########################################################################

@app.route('/')
def index():
    if ("//radiowut.herokuapp.com/" in request.url_root
    and request.headers.get("X-Forwarded-Proto", "http") != "https"):
        return redirect("https://radiowut.herokuapp.com/", 301)

    username = request.args.get('username', '')
    if username:
        username = escape(username[:100].replace(" ","-").lower().strip())

        return redirect(
            url_for('userview', username=username),
            301
        )

    return render_template("index.html",
        google_analytics_id=google_analytics_id()
    )

###########################################################################

@app.route('/<username>/')
def userview(username):
    if ("//radiowut.herokuapp.com/" in request.url_root
    and request.headers.get("X-Forwarded-Proto", "http") != "https"):
        return redirect(
            "https://radiowut.herokuapp.com%s" % url_for('userview', username=(username)),
            301
        )

    new_username = username[:100].lower().strip()
    if username != new_username:
        return redirect(
            url_for('userview', username=new_username),
            301
        )

    view_cachekey = "userview6(username=%s)" % username
    output = cache_get(view_cachekey)
    if not output:
        user_key = user_key_for_username(username)
        if user_key == 0:
            output = ("Unknown user", 404, {'Content-Type': 'text/plain'})
            cache_set(view_cachekey, output, 3600)
            return output
        try:
            artist_key_set = artists_in_user_collection(user_key)
        except:
            artist_key_set = []

        new_releases = get_new_releases()

        user_new_releases = filter(
            lambda release: release.get("artistKey", "").split("|", 1)[0] in artist_key_set,
            new_releases
        )
        output = render_template("user_new_releases.html",
            username=username,
            user_new_releases=user_new_releases,
            google_analytics_id=google_analytics_id()
        )
        cache_set(view_cachekey, output, 21600)

    return output

###########################################################################

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))

    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })
    app.run(host='0.0.0.0', port=port)
