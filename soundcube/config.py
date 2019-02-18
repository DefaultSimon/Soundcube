# coding=utf-8
import logging
import os
import configparser

log = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("data/settings.ini")

player_c = configparser.ConfigParser()
player_c.read("data/player.ini")

HOST = config.get("Server", "host", fallback="localhost")
PORT = config.getint("Server", "port", fallback=5000)

# YouTube API key
BACKEND_API_KEY = config.get("APIs", "googleApiKey", fallback=None)
FRONTEND_API_KEY = config.get("APIs", "frontend_googleApiKey", fallback=None)
if not BACKEND_API_KEY:
    raise RuntimeError("'googleApiKey' is missing in the config file!")
if not FRONTEND_API_KEY:
    raise RuntimeError("'frontend_googleApiKey' is missing in the config file!")

# Frontend build location
FRONTEND_BUILD_LOCATION = config.get("Routes", "build_location", fallback=None)
if not FRONTEND_BUILD_LOCATION:
    raise RuntimeError("'build_location' is missing in the config file!")
else:
    FRONTEND_BUILD_LOCATION = os.path.abspath(FRONTEND_BUILD_LOCATION)

PUBLIC_URL = config.get("Server", "public_url", fallback="localhost")
if PUBLIC_URL in ("0.0.0.0", "localhost", "127.0.0.1"):
    log.warning(f"'PUBLIC_URL' is set to '{PUBLIC_URL}', this is for development use only!")

# Player-related
DEFAULT_VOLUME = player_c.getint("Player", "default_volume", fallback=50)
VOLUME_STEP = player_c.get("Player", "volume_change_step", fallback=5)

API_ROUTE_PREFIX = config.get("Routes", "api_prefix", fallback="/api/v1")


def get_config(section, key):
    return config.get(section, key)
