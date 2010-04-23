from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext

from piston.models import Consumer
from api.forms import CreateOauthAccessForm
from django.shortcuts import render_to_response as render
from piston.forms import OAuthAuthenticationForm

@login_required
def create_api_access(request):
    """Display the form to make a API access demand.
    
    """
    if request.POST:
        form = CreateOauthAccessForm(data=request.POST)
        if form.is_valid():
            model = form.save()
            model.user = request.user
            model.generate_random_codes()
            return HttpResponseRedirect(reverse('api:listaccess'))
    else:    
        form = CreateOauthAccessForm()
    
    return render('oauth/access.html', {
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def list_api_access(request):
    """List the API access for the connected user
    
    """
    consumers = Consumer.objects.filter(user=request.user)
    
    return render('oauth/access_list.html', {
        'consumers': consumers
    }, context_instance=RequestContext(request))
    
def oauth_auth_view(request, token, callback, params):
    form = OAuthAuthenticationForm(initial={
        'oauth_token': token.key,
        'oauth_callback': token.get_callback_url() or callback,
      })

    return render('oauth/authorize_token.html',{
         'form': form 
    }, context_instance=RequestContext(request))
