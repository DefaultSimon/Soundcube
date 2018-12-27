# coding=utf-8
from quart import Quart

app = Quart(__name__)

# Load the default config and overwrite with custom one (if provided)
app.config.from_pyfile("soundcube/quartconfig_defaults.ini")
app.config.from_pyfile("data/quartconfig.ini", silent=True)

@app.route('/')
async def hello():
    return 'Hello World'


# Run with `run.bat` (or `hypercorn server:app`)
