import falcon

from opensecurities.endpoints import BaseEndPoint

class Status(BaseEndPoint):

    path = '/status'

    def on_get(self, req, resp):

        resp.body = 'Everything is working'
