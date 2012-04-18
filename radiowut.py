import os
from rdioapi import Rdio
from cacheutil import cache_get, cache_set
import threading
_locals = threading.local()

__all__ = [
    'user_key_for_username',
    'artists_in_user_collection',
    'get_new_releases'
]

def get_rdio():
    rdio_cli = getattr(_locals, "rdio_cli", None)
    if rdio_cli:
        return rdio_cli

    rdio_cli = Rdio(
        os.environ.get('RDIO_KEY'),
        os.environ.get('RDIO_SHARED_SECRET'),
        {}
    )
    _locals.rdio_cli = rdio_cli
    return rdio_cli

def user_key_for_username(username):
    u_cachekey = "user_key(username=%s)" % username
    user_key = cache_get(u_cachekey)
    if not user_key:
        r = get_rdio()

        try:
            u_result = r.findUser(vanityName=username)
            user_key = u_result.get("key", None)
        except:
            user_key = None

        if not user_key:
            cache_set(u_cachekey, 0, 300)
            return 0

        cache_set(u_cachekey, user_key, 86400*90)

    return user_key

def artists_in_user_collection(user_key):
    user_artists_cachekey = "user_artists2(user_key=%s)" % user_key
    artist_key_set = cache_get(user_artists_cachekey)
    if not artist_key_set:
        r = get_rdio()
        artist_result = r.getArtistsInCollection(user=user_key)
        artist_key_set = frozenset([
            artist.get("artistKey", "") for artist in artist_result
        ])
        cache_set(user_artists_cachekey, artist_key_set, 86400)
    return artist_key_set

def get_new_releases():
    releases_cachekey = "new_releases3()"
    new_releases = cache_get(releases_cachekey)
    if not new_releases:
        r = get_rdio()
        new_releases = []
        #new_releases += r.getNewReleases()
        new_releases += r.getNewReleases(time="thisweek")
        new_releases += r.getNewReleases(time="lastweek")
        new_releases += r.getNewReleases(time="twoweeks")
        cache_set(releases_cachekey, new_releases, 21600)
    return new_releases
