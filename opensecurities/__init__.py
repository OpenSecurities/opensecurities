from flask import Flask

app = Flask(__name__)

from opensecurities.endpoints import status
