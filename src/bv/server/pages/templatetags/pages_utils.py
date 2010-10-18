from django import template
from bv.server.pages.models import Category, EnhancedFlatPage
register = template.Library()

class GetPagesLinksForCategory(template.Node):
    """Get the html list of links for each page of a specified category.
    
    """
    def __init__(self, category, varname):
        self.category_name = category
        self.varname = varname
        
    def render(self, context):
        """Add a list of matching elements to the context, using the varname var.
        
        >>> c = {}
        >>> o = GetPagesLinksForCategory('unexistant', 'context')
        >>> o.render(c)
        u''
        >>> c
        {'context': []}
        """
        if self.category_name == "all":
            flatpages = EnhancedFlatPage.objects.all()
        else :
            category = Category.objects.filter(name=self.category_name)
            
            if not category:
                flatpages = []
            else:
                flatpages = EnhancedFlatPage.objects.filter(category=category)
            
        context[self.varname] = flatpages
        return u''
        
@register.tag
def flatpages(parser, token):
    """
    Template tag for displaying the list of links of a specified category.
    
    Usage::
    
        {% flatpages "category" as var %}
        {% flatpages as var %}
        
    Category can be left blank, and in this case, all registered pages will be 
    returned
    
    """
    tokens = token.contents.split()
    category = "'all'"
    
    if len(tokens) == 3:
        varname = tokens[2]
    elif len(tokens) == 4: 
        category = tokens[1]
        varname = tokens[3]
    else:
        raise template.TemplateSyntaxError, "%r tag accepts 2 or 3 arguments" % tokens[0]
    
        
    if not (category[0] == category[-1] and category[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's category argument should be in quotes" % tokens[0]
            
    return GetPagesLinksForCategory(category[1:-1], varname)
