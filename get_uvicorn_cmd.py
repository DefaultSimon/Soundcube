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
arg_list.append("--host {} --port {}".format(HOST, PORT))

# Whether to turn on debug mode
LOG_LEVEL = config.get("Server", "log_level", fallback=False)
if LOG_LEVEL:
    arg_list.append(f"--log-level {LOG_LEVEL}")


# Add the app location at the end
arg_list.append(APP)

# Output the full command
print("uvicorn " + " ".join(arg_list), flush=True, end="")
