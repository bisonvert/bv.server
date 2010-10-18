from bv.server.api.handlers import Handler, AnonymousHandler
from piston.utils import rc, require_mime, require_extended
from piston.utils import validate

from django.contrib.auth.models import User
from bv.server.accounts.models import UserProfile

class AnonymousUsersHandler(AnonymousHandler):
    """Handler for accessing anonymously to user informations.
    
    """
    def read(self, request, user_id=None):
        try:
            if not user_id.encode().isdigit():
                return rc.BAD_REQUEST
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            return {
                'id': user.id,
                'username': user.username,
                'driver_km_price': profile.driver_km_price,
                'driver_smokers_accepted': profile.driver_smokers_accepted,
                'driver_pets_accepted': profile.driver_pets_accepted,
                'driver_place_for_luggage': profile.driver_place_for_luggage,
                'driver_car_type': profile.driver_car_type, 
                'driver_seats_available': profile.driver_seats_available,
                'passenger_max_km_price': profile.passenger_max_km_price,
                'passenger_smokers_accepted': profile.passenger_smokers_accepted,
                'passenger_pets_accepted': profile.passenger_pets_accepted,
                'passenger_place_for_luggage': profile.passenger_place_for_luggage,
                'passenger_car_type': profile.passenger_car_type,
                'passenger_min_remaining_seats': profile.passenger_min_remaining_seats,     
            }
        except User.DoesNotExist:
            return rc.NOT_HERE
    
class UsersHandler(Handler):
    """Handler for accessing user informations, when authenticated.
    
    """
    anonymous = AnonymousUsersHandler
    model = User
    
    def create(self, request):
        return rc.OK
        
    def read(self, request, user_id=None):        
        if user_id == 'active' and request.user:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'phone': profile.phone,
                'mobile_phone': profile.mobile_phone,
                'home_address': profile.home_address,
                'home_address2': profile.home_address2,
                'home_zipcode': profile.home_zipcode,
                'home_city': profile.home_city,
                'alert': profile.alert,
                'driver_km_price': profile.driver_km_price,
                'driver_smokers_accepted': profile.driver_smokers_accepted,
                'driver_pets_accepted': profile.driver_pets_accepted,
                'driver_place_for_luggage': profile.driver_place_for_luggage,
                'driver_car_type': profile.driver_car_type, 
                'driver_seats_available': profile.driver_seats_available,
                'passenger_max_km_price': profile.passenger_max_km_price,
                'passenger_smokers_accepted': profile.passenger_smokers_accepted,
                'passenger_pets_accepted': profile.passenger_pets_accepted,
                'passenger_place_for_luggage': profile.passenger_place_for_luggage,
                'passenger_car_type': profile.passenger_car_type,
                'passenger_min_remaining_seats': profile.passenger_min_remaining_seats,
                'language': profile.language,
            }
        return self.anonymous.read(AnonymousUsersHandler(), request, user_id)
