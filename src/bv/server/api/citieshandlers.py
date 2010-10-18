#django imports
from django.template.defaultfilters import slugify

#piston imports
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

#api imports
from bv.server.api.handlers import Handler, AnonymousHandler

# bv imports
from bv.server.carpool.models import City


class CitiesHandler(AnonymousHandler):
    """Handler for accessing anonymously to user informations.
    
    """
    def read(self, request, query):
        return City.objects.filter(slug__startswith=slugify(query)).order_by('-population', 'slug')[:15]
