# coding=utf-8
######################
# Hypercorn Command
# This script puts together hypercorn arguments for use in e.g. a batch script
# The batch script receives the arguments via stdout
######################

from soundcube.config import config

APP = config.get("Server", "app")

HOST = config.get("Server", "host")
PORT = config.get("Server", "port")
binds = "{}:{}".format(HOST, PORT)

command = "hypercorn --bind {binds} {app}".format(binds=binds, app=APP)

# Output the command
print(command, flush=True, end="")
