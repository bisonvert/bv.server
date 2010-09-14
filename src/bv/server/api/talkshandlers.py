from api.handlers import Handler, AnonymousHandler, paginate_items
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

from lib import LibTalks, exceptions
from talks.models import Talk, Message
from talks.forms import ContactUserForm

from django import forms
from django.conf import settings
from django.db.models import Q

class CreateTalkForm(ContactUserForm):
    trip_id = forms.IntegerField()

__message_public_fields__ = (
'id',
'date', 
'message', 
'talk', 
'from_user',
)

__talk_public_fields__ = (
'id', 
'creation_date', 
('trip',(
    'id',
    'departure_city', 
    ('user',(
        'id', 
        'username',
    )),
    'arrival_city', 
    'date', 
    'time',
)),
('from_user',(
    'id', 
    'username',
))
)

class BaseTalkHandler(Handler):
    allowed_methods = ('GET', 'PUT', 'DELETE', 'POST')
    count = settings.DEFAULT_PAGINATION_COUNT
    def __init__(self):
        self.lib = LibTalks()

class TalksHandler(BaseTalkHandler):
    model = Talk
    fields = __talk_public_fields__
    
    @validate(CreateTalkForm)
    def create(self, request):
        """Initiate the talk with another user.
        
        """
        params = dict(request.REQUEST.items())
        if "trip_id" in params:
            trip_id = params['trip_id']
        else:
            return rc.BAD_REQUEST  
        try:
            talk = self.lib.contact_user(request.user, trip_id, params)
            return talk.id
        except exceptions.TalkAlreadyExists:
            return rc.DUPLICATE_ENTRY
        except exceptions.InvalidMail:
            return rc.FORBIDDEN
        except exceptions.TripDoesNotExist:
            return rc.NOT_HERE
                    
    def read(self, request, talk_id=None, start=None, count=None):
        """List all talks for the authenticated user
        
        """
        if 'trip_id' in request.GET:
            # get the trip
            talks = Talk.objects.filter(Q(trip__id=request.GET['trip_id']) 
                & (Q(trip__user__id=request.user.id) | 
                        Q(from_user__id=request.user.id)))
            return talks

        if talk_id == 'count':
            return self.lib.list_talks(request.user).count()
        elif talk_id is not None:
            talk = Talk.objects.get(id=talk_id)
            user = request.user
            if (talk.from_user.id != user.id and talk.trip.user.id != user.id):
                return rc.FORBIDDEN
            return talk;
        else:
            items = self.lib.list_talks(request.user)
            return paginate_items(items, start, count, request, self.count)
        
    def update(self, request, talk_id):
        """Validate or cancel the talk
        
        """
        params = dict(request.REQUEST.items())
        if "validate" in params and params['validate'] in ('true', 'True', True):
            self.lib.validate_talk(request.user, talk_id)
            return rc.ALL_OK
        elif "cancel" in params and params['cancel'] in ('true', 'True', True):
            try:
                self.lib.cancel_talk(request.user, talk_id, params)
                return rc.DELETED
            except exceptions.TalkDoesNotExist:
                return rc.NOT_HERE
        else:
            return rc.BAD_REQUEST       
        
        
class MessagesHandler(BaseTalkHandler):
    model = Message
    fields = __message_public_fields__
    def read(self, request, message_id=None, talk_id=None, start=None, 
            count=None):
        """List all messages for a talk, or a specific message.
        
        """
        if message_id == "count":
            try:
                return self.lib.list_messages(request.user, talk_id).count() 
            except exceptions.InvalidUser:
                return rc.FORBIDDEN
        elif message_id is not None:
            try:
                message = Message.objects.get(id=talk_id)
                user = request.user
                if (message.talk.from_user.id != user.id and message.talk.trip.user.id != user.id):
                    return rc.NOT_HERE
                else:
                    return message                 
            except (Message.DoesNotExist):
                return rc.NOT_HERE
        else:
            try:
                items = self.lib.list_messages(request.user, talk_id)
                return paginate_items(items, start, count, request, self.count)
            except exceptions.TalkDoesNotExist:
                 return rc.NOT_HERE
    
    @validate(ContactUserForm)
    def create(self, request, talk_id):
        """Add a message
        
        """
        try:
            self.lib.add_message(request.user, talk_id,
                dict(request.REQUEST.items()))
            return rc.ALL_OK            
        except exceptions.TalkDoesNotExist:
            return rc.NOT_HERE
        except exceptions.InvalidUser:
            return rc.FORBIDDEN
