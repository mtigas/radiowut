## fun rdio bits

Currently:

* A page that displays only the new releases for artists in a given user's
  collection.

**CAVEAT**: I am still *just* learning both [Flask](http://flask.pocoo.org/)
and the [Rdio API](http://developer.rdio.com/). This is a totally incomplete
scratchpad-ish project.

TODO: l2 flask/jinja template because [this is currently super stupid][dumb]

[dumb]: https://github.com/mtigas/radiowut/blob/master/app.py#L15

## Instructions

* Hit up the [Rdio Developers Site](http://developer.rdio.com/) and see the
  **how to get started** portion. Register there and grab an "API key" and
  "API shared secret".
* Get an account with [Heroku](https://www.heroku.com/).

Start a local python project like so. (I like to put my projects in a `~/Code`
directory. You can change that to whatever.)

    cd ~/Code/
    virtualenv --no-site-packages radiowut
    cd radiowut
    echo "export PIP_RESPECT_VIRTUALENV=true" >>| bin/activate
    echo "export RDIO_KEY=\"your_api_key_here\"" >>| bin/activate
    echo "export RDIO_SHARED_SECRET=\"your_shared_secret_here\"" >>| bin/activate
    source bin/activate

    git clone git://github.com/mtigas/radiowut.git repo
    cd repo
    pip install -r requirements.txt

You should be able to run `python app.py`. (Caveat: actually, you'll probably
also need a local memcached installation to go with it.)

To deploy into Heroku: (You will need to change the app name from `radiowut`
since I'm already using that one. ;) )

    heroku create radiowut --stack cedar
    heroku config:add RDIO_KEY=your_api_key_here
    heroku config:add RDIO_SHARED_SECRET=your_shared_secret_here
    heroku addons:add memcache
    git push heroku master
