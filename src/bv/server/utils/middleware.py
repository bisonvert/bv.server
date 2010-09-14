# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""Middlewares pour le projet Ecov."""

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.contrib.sessions.models import Session
from django.db import connection
import datetime


class QueryLoggerMiddleware(object):
    """Middleware pour logguer les requêtes SQL exécutées lors d'une requête
    HTTP.

    Paramètres à définir dans les settings:

    + SQL_LOG_PATHFILE: chemin absolu vers le fichier de logs.
    + SQL_LOG: active ou non les logs.

    Ne fonctionne qu'avec le mode DEBUG activé.

    """
    def process_response(self, request, response):
        """Trace toutes les requêtes SQL exécutées lors d'une requête HTTP
        dans un fichier de logs.

        """
        if not settings.SQL_LOG:
            return response
        log_file = None
        try:
            log_file = open("%s" % settings.SQL_LOG_PATHFILE, mode= 'a')
            sql_queries = connection.queries
            for i in range(len(sql_queries)):
                query = sql_queries[i]
                log_file.write("#%d %s\n" % (i, query['time']))
                log_file.write("%s\n" % query['sql'])
        finally:
            if log_file:
                log_file.flush()
                log_file.close()

        return response

class EcovSessionMiddleware(object):
    """Middleware pour les sessions.

    Permet d'avoir des sessions permanentes: le cookie de session stocké sur le
    client n'expire pas à la fermeture du client.

    Paramètres à définir dans les settings (en plus des paramètres habituels,
    voir http://www.djangoproject.com/documentation/sessions/#settings):

    + PERSISTENT_SESSION_KEY: nom de la clé en session qui indique si la
      session doit être permanente ou non.

    """
    def process_request(self, request):
        """Initialise l'objet Session Engine et l'objet Session."""
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        request.session = engine.SessionStore(
            request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        )

    def process_response(self, request, response):
        """Définit le cookie de session.

        Met à jour l'objet session.

        """
        # If request.session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        try:
            modified = request.session.modified
            accessed = request.session.accessed
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if not request.session.get(settings.PERSISTENT_SESSION_KEY,
                        False):
                    # session will expire when the user closes the browser
                    max_age = None
                    expires = None
                    db_session_max_age = settings.SESSION_COOKIE_AGE
                else:
                    max_age = settings.SESSION_PERSISTENT_COOKIE_AGE
                    expires = datetime.datetime.strftime(
                        (datetime.datetime.utcnow() +
                            datetime.timedelta(
                                seconds=settings.SESSION_PERSISTENT_COOKIE_AGE
                            )),
                        "%a, %d-%b-%Y %H:%M:%S GMT"
                    )
                    db_session_max_age = settings.SESSION_PERSISTENT_COOKIE_AGE

                Session.objects.save(
                    request.session.session_key,
                    request.session._session,
                    (datetime.datetime.now() +
                        datetime.timedelta(seconds=db_session_max_age))
                )
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key,
                    max_age=max_age,
                    expires=expires,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE or None
                )
        return response

class ProxyHeadersRemoveMiddleware(object):
    """Middleware pour supprimer l'entrée HTTP_X_FORWARDED_HOST du dictionnaire
    META de l'objet request.

    A utiliser avec un proxy Apache SSL pour éviter les problèmes de redirect.

    """
    def process_request(self, request):
        """Supprime l'entrée HTTP_X_FORWARDED_HOST du dictionnaire META de
        l'objet request.

        """
        if 'HTTP_X_FORWARDED_HOST' in request.META:
            del request.META['HTTP_X_FORWARDED_HOST']

