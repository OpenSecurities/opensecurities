import json

from opensecurities import app
from opensecurities.endpoints import render
from opensecurities.version import __version__ as VERSION

@app.route('/status')
def index():
    data = {
        'version' : VERSION
    }

    return render(data)
