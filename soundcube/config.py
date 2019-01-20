# coding=utf-8
import configparser

config = configparser.ConfigParser()
config.read("data/settings.ini")

player_c = configparser.ConfigParser()
player_c.read("data/player.ini")

# YouTube API key
BACKEND_API_KEY = config.get("APIs", "googleApiKey", fallback=None)
FRONTEND_API_KEY = config.get("APIs", "frontend_googleApiKey", fallback=None)
if not BACKEND_API_KEY:
    raise RuntimeError("'googleApiKey' is missing in the config file!")
if not FRONTEND_API_KEY:
    raise RuntimeError("'frontend_googleApiKey' is missing in the config file!")

# Player-related
DEFAULT_VOLUME = config.get("Player", "default_volume", fallback=50)
VOLUME_STEP = config.get("Player", "volume_change_step", fallback=5)


def get_config(section, key):
    return config.get(section, key)
