r"""
>>> from django.contrib.auth.models import User
>>> from lib.libcarpool import LibCarpool
>>> from django.utils.datastructures import MultiValueDict
>>> from bv.server.carpool.models import Trip
>>> import datetime

### Carpool ###

>>> lc = LibCarpool()

Get details of a trip. this convert arrival and departure point into a dict of
values.
>>> details = lc.get_trip_details(u'paris', 75, u'toulouse', 31)
>>> details
{'arrival': {'favoriteplace': None, 'name': u'Toulouse (31)', 'point': 'POINT (1.4333330000000000 43.6000000000000014)'}, 'departure': {'favoriteplace': None, 'name': u'Paris (75)', 'point': 'POINT (2.3333330000000001 48.8666669999999996)'}}

With these details, it's now possible to get a geometry (polygon):
>>> lc.get_trip_geometry_from_details(details)
'POLYGON ((1.4333330000000000 43.6000000000000014, 2.3333330000000001 43.6000000000000014, 2.3333330000000001 48.8666669999999996, 1.4333330000000000 48.8666669999999996, 1.4333330000000000 43.6000000000000014))'

It's also possible to pass directly the values to get_trip_details.
>>> lc.get_trip_geometry_from_details(departure_slug=u'paris', departure_zip=75, arrival_slug=u'toulouse', arrival_zip=31)
'POLYGON ((1.4333330000000000 43.6000000000000014, 2.3333330000000001 43.6000000000000014, 2.3333330000000001 48.8666669999999996, 1.4333330000000000 48.8666669999999996, 1.4333330000000000 43.6000000000000014))'

>>> lc.get_city(u"toulouse", 31)
<City: Toulouse (31)>

>>> lc.get_city(u"unexisting_city", 00)
Traceback (most recent call last):
...
CityNotFound

>>> lc.list_trips()
[<Trip: test - lavaur / paris - offre>, <Trip: test - toulouse / paris - demande>]        

>>> lc.list_trips_with_departure_or_arrival(lc.get_city('toulouse', 31), True, 'date')
[<Trip: test - toulouse / paris - demande>]

>>> paginator = lc.get_trip_list_paginator_with_departure_or_arrival(lc.get_city('toulouse', 31), True, 'date', 1, 10, [10,20,30])
>>> paginator.__class__
<class 'utils.paginator.PaginatorRender'>
>>> paginator.page
1

>>> lc._get_pagination_url(3)
'?pg=3'

>>> lc._get_pagination_url_with_order(3, 'date')
'?pg=3&order=date'


>>> user = User.objects.get(username="test")
>>> lc.list_trips_by_user(user, "date")
[<Trip: test - lavaur / paris - offre>, <Trip: test - toulouse / paris - demande>]

>>> user = User.objects.get(username="test")
>>> valid_data = MultiValueDict({u'comment': [u''], u'demand-passenger_max_km_price': [u''], u'offer-radius': [u'500'], u'arrival_point': [u'POINT(2.3509871 48.85666670000002)'], u'interval_max': [u'0'], u'demand-passenger_smokers_accepted': [u'on'], u'offer-steps': [u''], u'trip_type': [u'1'], u'demand-passenger_pets_accepted': [u'on'], u'interval_min': [u'7'], u'demand-radius': [u'500'], u'demand-passenger_min_remaining_seats': [u''], u'return_trip': [u'false'], u'departure_point': [u'POINT(1.4429513 43.60436300000001)'], u'time': [u'8'], u'arrival_address': [u''], u'baseLayers': [u'Google - plan'], u'regular': [u'False'], u'departure_city': [u'toulouse'], u'date': [u'20/01/2010'], u'D\xe9part / Arriv\xe9e / Points de passage': [u'D\xe9part / Arriv\xe9e / Points de passage'], u'alert': [u'on'], u'departure_address': [u''], u'name': [u'announce name'], u'Trajets / Zones de recherche': [u'Trajets / Zones de recherche'], u'demand-passenger_car_type': [u''], u'offer-route': [u''], u'arrival_city': [u'paris']})
>>> datas = lc.create_trip(user, valid_data)
>>> datas['trip']
<Trip: test - announce name>
>>> datas['trip'].offer
>>> datas['form_demand'].is_valid()
True
>>> datas['form_trip'].is_valid()
True

>>> created_trip = Trip.objects.get(name="announce name")
>>> created_trip
<Trip: test - announce name>

>>> lc.delete_trip(created_trip.id, user)

>>> datas = lc.create_trip(user, {})
>>> datas['error']
True

>>> valid_data = MultiValueDict({u'comment': [u''], u'demand-passenger_max_km_price': [u''], u'offer-radius': [u'500'], u'arrival_point': [u'POINT(2.3509871 48.85666670000002)'], u'interval_max': [u'0'], u'demand-passenger_smokers_accepted': [u'on'], u'offer-steps': [u''], u'trip_type': [u'1'], u'demand-passenger_pets_accepted': [u'on'], u'interval_min': [u'7'], u'demand-radius': [u'15000'], u'demand-passenger_min_remaining_seats': [u''], u'return_trip': [u'false'], u'departure_point': [u'POINT(1.4429513 43.60436300000001)'], u'time': [u'9'], u'arrival_address': [u''], u'baseLayers': [u'Google - plan'], u'regular': [u'False'], u'departure_city': [u'toulouse'], u'date': [u'24/01/2010'], u'D\xe9part / Arriv\xe9e / Points de passage': [u'D\xe9part / Arriv\xe9e / Points de passage'], u'alert': [u'on'], u'departure_address': [u''], u'name': [u'toulouse / paris - demande'], u'Trajets / Zones de recherche': [u'Trajets / Zones de recherche'], u'demand-passenger_car_type': [u''], u'offer-route': [u''], u'arrival_city': [u'paris']})
>>> temp = lc.update_trip(user, valid_data, 28)
>>> Trip.objects.get(id=28).date
datetime.date(2010, 1, 24)

There is two ways to find information; both of them needs that you give
some information about *your* trip. This is possible by specifying the
ID of an existing trip, or by specifiying all the useful data

>>> lc.get_trip_results(trip_id=27, user=User.objects.get(username="test"))
{'trip_demands': [<Trip: test - toulouse / paris - demande>], 'trip_offers': None, 'trip': <Trip: test - lavaur / paris - offre>}

And by specifying useful data. Here, imagine that we are seeking for a way
to go from Toulouse to Paris, on 25. jan. 2010. 

>>> paris = lc.get_city(u'paris', 75).point
>>> toulouse = lc.get_city(u'toulouse', 31).point
>>> lc.get_trip_results(is_demand=True, departure_point=toulouse, arrival_point=paris, date=datetime.date(2010, 1, 20), demand_radius=2000)
{'trip': None,
 'trip_demands': None,
 'trip_offers': [<Trip: test - lavaur / paris - offre>]}
 
>>> user = User.objects.get(username='test2')
>>> lc.delete_trip(27, user)
Traceback (most recent call last):
    ... 
InvalidUser: given user have no rights to delete this trip                        

### Ratings ###

>>> lr = LibRating()
>>> user = User.objects.get(username="test")
>>> [(r.user, r.from_user, r.creation_date, r.mark) for r in lr.list_reports_for_user(user)]
[(<User: test>, <User: alexis>, datetime.date(2010, 1, 26), 5)]
        
>>> [(r.user, r.from_user, r.creation_date, r.mark) for r in lr.list_reports_from_user(user)]
[(<User: alexis>, <User: test>, datetime.date(2010, 1, 26), 5)]

>>> [(tr.user1, tr.user2, tr.departure_city, tr.arrival_city) for tr in lr.list_tempreports_for_user(user)]
[(<User: test>, <User: test>, u'toulouse', u'paris'), (<User: alexis>, <User: test>, u'Lavaur (81)', u'Paris')]    

>>> tr =lr.rate_user(user, 3, {'mark':'5','comment':'my comment'})
>>> tr.report2_mark 
u'5'

### Talks ###

>>> lt = LibTalks()
>>> lt.list_talks(user)
[]
>>> lt.contact_user(user, 27, {'message':"my message"})
<Talk: Talk object>
>>> lt.list_talks(user)
[<Talk: Talk object>]
>>> talk_id = lt.list_talks(user)[0].id
>>> [m.message for m in lt.list_messages(user, talk_id)]
[u'my message']

>>> lt.add_message(user, talk_id, {'message': 'the second message'})
>>> [m.message for m in lt.list_messages(user, talk_id)]
[u'my message', u'the second message']

>>> lt.cancel_talk(user, talk_id, {'message': 'explaination message'})
>>> lt.list_talks(user)
[]
>>> lt.contact_user(user, 27, {'message':"my message"})
>>> talk_id = lt.list_talks(user)[0].id
>>> lt.validate_talk(user, talk_id)
>>> lt.list_talks(user)
[]

"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
