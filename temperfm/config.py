import os
import json


DEFAULT_CONFIG_PATH = os.path.expanduser('~/.temperfm/config.json')
DEFAULT_CACHE_PATH = './cache.sqlite'
DEFAULT_LOG_PATH = './activity.log'
DEFAULT_PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'default_profile.json')
DEFAULT_LASTFM_KEY = ''

config_name = os.path.basename(DEFAULT_CONFIG_PATH)
config_dir = os.path.dirname(DEFAULT_CONFIG_PATH)
cache_path = os.path.join(config_dir, DEFAULT_CACHE_PATH)
log_path = os.path.join(config_dir, DEFAULT_LOG_PATH)
profile_path = os.path.join(config_dir, DEFAULT_PROFILE_PATH)
lastfm_key = DEFAULT_LASTFM_KEY


def load(path=DEFAULT_CONFIG_PATH):
    """
    :type path: str
    """
    global config_name, config_dir, cache_path, log_path, profile_path, lastfm_key

    if not os.path.isfile(path):
        raise RuntimeError(f'Unable to find config path: {path}')

    config_data = {}
    valid_config = False

    try:
        config_data = json.load(open(path))
        if isinstance(config_data, dict) and 'lastfm_key' in config_data:
            valid_config = True
    except json.JSONDecodeError:
        pass

    if not valid_config:
        raise RuntimeError('Config file must be a dictionary with at least "lastfm_key" defined')

    config_name = os.path.basename(path)
    config_dir = os.path.dirname(path)
    cache_path = os.path.join(config_dir, config_data.get('cache_path', DEFAULT_CACHE_PATH))
    log_path = os.path.join(config_dir, config_data.get('log_path', DEFAULT_LOG_PATH))
    profile_path = os.path.join(config_dir, config_data.get('profile_path', DEFAULT_PROFILE_PATH))
    lastfm_key = config_data.get('lastfm_key', DEFAULT_LASTFM_KEY)

    from . import profile

    profile.load(profile_path)
