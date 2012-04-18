import os
from flask import Flask, request, redirect, url_for, escape

app = Flask(__name__)


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

    return """<!doctype html><html><head><meta charset="utf-8">"""+analytics_code()+"""</head><body>
        <h1>Anything new by the artists I listen to?</h1>
        <p>Tired of sifting through Rdio's "New Releases" tab? Find the latest releases
        for <i>just</i> the artists in your collection:</p>
        <form action="" method="get">
        Rdio Username: <input type="text" name="username" placeholder="my-rdio-username"/><br>
        <input type="submit" value="Submit"/>
        </form>
        <p>(This should <a href="https://twitter.com/idangazit/status/191800690732044290">really be a feature in Rdio proper</a>, eh?)</p>
        <p><a href="https://github.com/mtigas/radiowut">This project is on GitHub</a>.<br>&copy; 2012 Mike Tigas; <a href="http://mike.tig.as/">web</a>, <a href="https://twitter.com/mtigas">twitter</a>, <a href="http://www.rdio.com/people/mtigas/">rdio</a></p>
    """

###########################################################################
from cacheutil import cache_get, cache_set
from radiowut import (user_key_for_username, artists_in_user_collection,
    get_new_releases)


def analytics_code():
    try:
        ga_id = os.environ.get('GA_ANALYTICS_ID', None)
    except:
        ga_id = None

    if not ga_id:
        return ""

    return """<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s'], ['_trackPageview'], ['_setSiteSpeedSampleRate', 100]);
  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>""" % ga_id


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

    view_cachekey = "userview4(username=%s)" % username
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
        output = """<!doctype html><html><head><meta charset="utf-8">"""+analytics_code()+"""</head><body>"""
        output += """<p>New releases (past two weeks) for artists in <b><a href="http://www.rdio.com/people/%s/">%s</a></b>'s <a href="http://www.rdio.com/people/%s/collection/">collection</a>:</p><hr>""" % (
            escape(username),
            escape(username),
            escape(username)
        )
        for release in user_new_releases:
            output += """
            <div style="width:220px;height:300px;text-align:center;padding:10px;margin:10px;float:left;overflow-y:auto">
                <a href="http://www.rdio.com%s"><img src="%s" alt="%s album cover"/></a><br>
                <a href="http://www.rdio.com%s"><b>%s</b></a><br>
                <a href="http://www.rdio.com%s"><i>%s</i></a><br>
                Released %s
            </div>""" % (
                release['url'],
                release['icon'],
                release['name'],
                release['url'],
                release['name'],
                release['artistUrl'],
                release['artist'],
                release['displayDate']
            )
        output += """<br style="clear:both"><hr>
        <p><a href="https://github.com/mtigas/radiowut">This project is on GitHub</a>.<br>&copy; 2012 Mike Tigas; <a href="http://mike.tig.as/">web</a>, <a href="https://twitter.com/mtigas">twitter</a>, <a href="http://www.rdio.com/people/mtigas/">rdio</a></p>"""
        cache_set(view_cachekey, output, 21600)

    return output

###########################################################################

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
