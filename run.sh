#!/usr/bin/env bash
# this captures the output of get_uvicorn_cmd.py
OUTPUT="$(pipenv run python get_uvicorn_cmd.py)"

# Don't show info about detecting a virtual env
set PIPENV_VERBOSITY=-1
pipenv run ${OUTPUT}