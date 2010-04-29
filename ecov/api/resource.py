from piston.resource import Resource as PistonResource
from piston.utils import rc
import json

class Resource(PistonResource):
    def form_validation_response(self, e):
        resp = rc.BAD_REQUEST
        resp.write(' ' + dict(e.form.errors.items()).__str__())
        return resp
