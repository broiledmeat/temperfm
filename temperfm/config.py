import os
import json


DEFAULT_CONFIG_DIRECTORY = os.path.expanduser('~/.temperfm')
DEFAULT_CONFIG_FILENAME = 'config.json'

config_path = None
cache_path = 'cache.sqlite'
log_path = 'activity.log'
lastfm_key = ''


def load(path=None):
    """
    :type path: str | None
    """
    global config_path, lastfm_key, cache_path, log_path

    if path is None:
        path = os.path.join(DEFAULT_CONFIG_DIRECTORY, DEFAULT_CONFIG_FILENAME)

    if path is None or not os.path.isfile(path):
        raise RuntimeError(f'Unable to find config path: {path}')

    config_path = path
    config_dir = os.path.dirname(config_path)

    conf = {}
    valid_config = False

    try:
        conf = json.load(open(path))
        if isinstance(conf, dict) and 'lastfm_key' in conf:
            valid_config = True
    except json.JSONDecodeError as e:
        pass

    if not valid_config:
        raise RuntimeError('Config file must be a dictionary with at least "lastfm_key" defined')

    lastfm_key = conf.get('lastfm_key', lastfm_key)
    cache_path = os.path.join(config_dir, conf.get('cache_path', cache_path))
    log_path = os.path.join(config_dir, conf.get('log_path', log_path))
