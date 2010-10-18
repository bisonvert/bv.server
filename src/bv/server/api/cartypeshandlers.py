#django imports
from django.template.defaultfilters import slugify

#piston imports
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

#api imports
from bv.server.api.handlers import Handler, AnonymousHandler

# bv imports
from bv.server.carpool.models import CarType

class CarTypesHandler(AnonymousHandler):
    """Handler for accessing cartypes.
    
    """
    def read(self, request):
        return CarType.objects.all()
