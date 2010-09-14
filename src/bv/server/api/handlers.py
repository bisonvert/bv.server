from piston.handler import BaseHandler as Handler, \
    AnonymousBaseHandler as AnonymousHandler
    
from django.contrib.auth.models import User

def paginate_items(items, start, count, request, defaultcount):
    if not start:
        start = int(request.GET.get('start', 0))
    if not count:
        count = int(request.GET.get('count', defaultcount))
    
    total = items.count()
    end = min (total, start + count)
    return items[start:end]
