import falcon
from falcon.testing import TestCase

from opensecurities.endpoints import status
from opensecurities import api

class TestStatusEndpoint(TestCase):
    
    def setUp(self):
        self.api = api

    def test_response(self):

        result = self.simulate_get('/status')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, 'Everything is working')
