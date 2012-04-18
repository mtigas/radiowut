# Some fun utilities to serialize python data into compressed strings.
# Need this because a) memcached has a 1MB datasize limit and b) memcached
# requires plain, ASCII-only strings.
try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads
from hashlib import md5
import os
import zlib
from base64 import b64encode, b64decode
import pylibmc
import threading
_locals = threading.local()

__all__ = [
    'get_cache_client',
    'get_key',
    'encode_value',
    'decode_value',
    'cache_get',
    'cache_set'
]

def get_cache_client():
    client = getattr(_locals, "cache_client", None)
    if client:
        return client

    try:
        on_heroku = (os.environ.get('MEMCACHE_SERVERS') and
            os.environ.get('MEMCACHE_USERNAME') and
            os.environ.get('MEMCACHE_PASSWORD'))
    except:
        on_heroku = False

    if on_heroku:
        client = pylibmc.Client(
            servers=[os.environ.get('MEMCACHE_SERVERS')],
            username=os.environ.get('MEMCACHE_USERNAME'),
            password=os.environ.get('MEMCACHE_PASSWORD'),
            binary=True
        )
    else:
        client = pylibmc.Client(servers=['127.0.0.1:55838'], binary=True)

    _locals.cache_client = client
    return client

def get_key(key):
    if type(key) == unicode:
        key = key.encode('utf-8')
    return md5(key).hexdigest()

###########################################################################

def encode_value(data, compression_level=1):
    serialized = dumps(data, -1)
    if compression_level:
        compressed = zlib.compress(serialized, compression_level)
    else:
        compressed = serialized
    coded = b64encode(compressed)
    return str(coded)

def decode_value(data):
    coded = str(data)
    compressed = b64decode(coded)
    return loads(zlib.decompress(compressed))

###########################################################################

def cache_get(key, default=None):
    """
    Gets a serialized 'rich data type' value from the database
    or returns `default` if the value did not exist or the value
    could not be parsed successfully.
    """
    mc = get_cache_client()
    try:
        return decode_value(mc.get(get_key(key))) or default
    except:
        return default

def cache_set(key, obj, timeout=None):
    mc = get_cache_client()
    try:
        mc.set(get_key(key), encode_value(obj), timeout)
    except:
        pass

    return obj

