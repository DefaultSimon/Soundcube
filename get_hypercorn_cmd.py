# coding=utf-8
######################
# Hypercorn Command
# This script puts together hypercorn arguments for use in e.g. a batch script
# The batch script receives the arguments via stdout
######################

from soundcube.config import config

arg_list = []

# Where the main file and app are located
APP = config.get("Server", "app")

# Which host:port to bind to
HOST = config.get("Server", "host")
PORT = config.get("Server", "port")
arg_list.append("--bind {}:{}".format(HOST, PORT))

# Whether to turn on the automatic reload for code changes
RELOAD = config.getboolean("Server", "reload_on_change")
if RELOAD is True:
    arg_list.append("--reload")

# Whether to turn on debug mode
DEBUG = config.getboolean("Server", "debug")
if DEBUG is True:
    arg_list.append("--debug")


# Add the app location at the end
arg_list.append(APP)

# Output the full command
print("hypercorn " + " ".join(arg_list), flush=True, end="")
