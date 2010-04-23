from api.handlers import Handler, AnonymousHandler
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

from rating.models import Report, TempReport
from rating.forms import ReportForm

from lib import LibRating
from lib.exceptions import InvalidUser

from django.contrib.gis.geos.geometry import GEOSGeometry
from datetime import date
from django.db.models import Q

__report_public_fields__ = (
'id',
'comment',     
'mark',
'creation_date', 
('user', (
    'username',
    'id',     
)),
('from_user',(
    'username',
    'id',     
)),
)

__tempreport_public_fields__ = (
'id', 
('user1',(
    'username',
    'id', 
)),
('user2',(
    'username',
    'id', 
)),
'end_date',
'start_date',
'report2_creation_date',
'report1_creation_date',
'dows',
'date',
'creation_date',
'type',
'departure_city',
'arrival_city',
)

class BaseRatingHandler(Handler):
    model = Report
    fields = __report_public_fields__
    def __init__(self):
        self.lib = LibRating()

class RatingsHandler(BaseRatingHandler):
    @validate(ReportForm)
    def create(self, request, tempreport_id):
        self.lib.rate_user(request.user, tempreport_id, request.POST)
        return rc.OK
        
    def read(self, request):
        return Report.objects.filter(Q(from_user=request.user) | Q(user=request.user))
        
class TempRatingsHandler(BaseRatingHandler):
    model = TempReport
    fields = __tempreport_public_fields__  
    def read(self, request, rating_id=None):
        ratings = TempReport.objects.get_user_tempreports(request.user)
        if rating_id:
            return ratings.filter(id=rating_id)
        else:
            return ratings
        
class MyRatingsHandler(BaseRatingHandler):
    def read(self, request):
        return self.lib.list_reports_from_user(request.user)
        
class RatingsAboutMeHandler(BaseRatingHandler):
    def read(self, request):
        return self.lib.list_reports_for_user(request.user)
