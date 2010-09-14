from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

def render_response(template_name, response_dict, request):
    """Render the response using the context.
    
    """
    
    template = loader.get_template(template_name)
    context = RequestContext(request, response_dict)
    return HttpResponse(template.render(context))
