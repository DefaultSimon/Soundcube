:: this captures the output of get_hypercorn_cmd.py
:: uses temp.txt as a temporary file for output, is deleted afterwards
pipenv run python get_hypercorn_cmd.py > temp.txt
set /p ARGS=<temp.txt

:: Don't show info about detecting a virtual env
set PIPENV_VERBOSITY=-1
del /s temp.txt  >nul 2>&1

pipenv run %ARGS%