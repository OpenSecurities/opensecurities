
import json
import unittest

from opensecurities import app
from opensecurities.version import __version__ as VERSION

class TestStatusEndpoint(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()

    def test_response(self):

        result = json.loads(self.app.get('/status').data.decode('utf-8'))
        self.assertEqual(VERSION, result['version'])
