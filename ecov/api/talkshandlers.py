from api.handlers import Handler, AnonymousHandler
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

from lib import LibTalks, exceptions
from talks.models import Talk, Message
from talks.forms import ContactUserForm

from django import forms
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
    def __init__(self):
        self.lib = LibTalks()

class TalksHandler(BaseTalkHandler):
    model = Talk
    fields = __talk_public_fields__
    
    @validate(CreateTalkForm)
    def create(self, request):
        """Initiate the talk with another user.
        
        """
        if "trip_id" in request.POST:
            trip_id = request.POST['trip_id']
        else:
            return rc.BAD_REQUEST  
        try:
            self.lib.contact_user(request.user, trip_id, request.POST)
            return rc.CREATED
        except exceptions.TalkAlreadyExists:
            return rc.DUPLICATE_ENTRY
        except exceptions.InvalidMail:
            return rc.FORBIDDEN
        except exceptions.TripDoesNotExist:
            return rc.NOT_HERE
                    
    def read(self, request, talk_id=None):
        """List all talkds for the authenticated user
        
        """
        if (talk_id is not None):
            talk = Talk.objects.get(id=talk_id)
            user = request.user
            if (talk.from_user.id != user.id and message.talk.trip.user.id != user.id):
                return rc.NOT_HERE
            return talk;
        else:
            return self.lib.list_talks(request.user)
        
    def update(self, request, talk_id):
        """Validate or cancel the talk
        
        """
        if "validate" in request.POST and request.POST['validate'] in ('true', 'True', True):
            self.lib.validate_talk(request.user, talk_id)
            return rc.ALL_OK
        elif "cancel" in request.POST and request.POST['cancel'] in ('true', 'True', True):
            try:
                self.lib.cancel_talk(request.user, talk_id, request.POST)
                return rc.DELETED
            except exceptions.TalkDoesNotExist:
                return rc.NOT_HERE
        else:
            return rc.BAD_REQUEST       
        
        
class MessagesHandler(BaseTalkHandler):
    model = Message
    fields = __message_public_fields__
    def read(self, request, talk_id, message_id=None):
        """List all messages for a talk, or a specific message.
        
        """
        if (message_id is None):
            try:
                return self.lib.list_messages(request.user, talk_id)
            except exceptions.TalkDoesNotExist:
                 return rc.NOT_HERE
        else:
            try:
                message = Message.objects.get(id=talk_id)
                user = request.user
                if (message.talk.from_user.id != user.id and message.talk.trip.user.id != user.id):
                    return rc.NOT_HERE
                else:
                    return message                 
            except (Message.DoesNotExist):
                return rc.NOT_HERE
    
    @validate(ContactUserForm)
    def create(self, request, talk_id):
        """Add a message
        
        """
        try:
            self.lib.add_message(request.user, talk_id, request.POST)
            return rc.ALL_OK            
        except exceptions.TalkDoesNotExist:
            return rc.NOT_HERE
        except exceptions.InvalidUser:
            return rc.FORBIDDEN
