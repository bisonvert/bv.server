# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Paginator helper"""

from django.template import RequestContext, loader
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, InvalidPage

DOT = '.'
ON_EACH_SIDE = 3
ON_ENDS = 2


class PaginatorRender(object):
    """Objet custom de pagination.

    Exemple d'utilisation dans une vue de type view(request, pagenum):
    ::

        queryset = Foo.objects.filter(bar=fooz).order_by('baz')
        paginator = PaginatorRender(
            queryset,
            pagenum,
            25,
            allow_empty_first_page=True,
            extra_context = {
                'foo': foo,
                'bar', bar,
            }
        )
        return paginator.render(request, 'path/to/template.html')

    """
    def __init__(self, queryset, page, pgnum, allow_empty_first_page=False,
            extra_context=None):
        """Paramètres:

        + queryset: un QuerySet
        + page: numéro de la page à afficher
        + pgnum: nombre d'items à afficher par page
        + allow_empty_first_page: si False et qu'il n'y a pas de résultat pour
          la page donnée, lève un 404
        + extra_context: contexte à passer au template

        """
        self.queryset = queryset
        self.page = int(page)
        self.pgnum = pgnum
        self.allow_empty_first_page = allow_empty_first_page
        self.extra_context = extra_context if extra_context is not None else {}
        self.paginator = None

    def render(self, request, templatepath):
        """Construit l'object Paginator (django.core.paginator.Paginator) et
        retourne le template compilé avec le contexte adapté.

        """
        self.paginator = Paginator(self.queryset, self.pgnum,
                allow_empty_first_page=self.allow_empty_first_page)
        try:
            page_obj = self.paginator.page(self.page)
        except InvalidPage:
            # TODO
            if not self.allow_empty_first_page and self.page == 1:
                raise Http404
            page_obj = self.paginator.page(1)

        response_dict = {
            'paginator': self.paginator,
            'page_obj': page_obj,
            'current_pg': self.pgnum,
        }
        response_dict.update(self.get_page_range_context())
        response_dict.update(self.extra_context)

        template = loader.get_template(templatepath)
        context = RequestContext(request, response_dict)
        return HttpResponse(template.render(context))

    def get_page_range_context(self):
        """From django.contrib.admin.templatetags.admin_list:pagination

        Utilisée pour populer le contexte de la Response, pour définir les
        pages dans le template.

        """
        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if self.paginator.num_pages <= 10:
            page_range = range(1, self.paginator.num_pages+1)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if self.page > (ON_EACH_SIDE + ON_ENDS + 1):
                page_range.extend(range(1, ON_EACH_SIDE))
                page_range.append(DOT)
                page_range.extend(range(self.page - ON_EACH_SIDE,
                    self.page + 1))
            else:
                page_range.extend(range(1, self.page + 1))
            if self.page < (self.paginator.num_pages - ON_EACH_SIDE - ON_ENDS):
                page_range.extend(range(self.page + 1,
                    self.page + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(range(self.paginator.num_pages - ON_ENDS + 1,
                    self.paginator.num_pages + 1))
            else:
                page_range.extend(range(self.page + 1,
                    self.paginator.num_pages + 1))
        return {'page_range': page_range, 'DOT': DOT}

