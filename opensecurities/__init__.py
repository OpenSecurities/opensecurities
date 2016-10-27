import falcon

from opensecurities.endpoints.status import Status

api = falcon.API()

# Status
api.add_route(Status.path, Status())
