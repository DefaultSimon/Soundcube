# coding=utf-8
from quart import Quart

app = Quart(__name__)


@app.route('/')
async def hello():
    return 'Hello World'


# Run with `run.bat` (or `hypercorn server:app`)
