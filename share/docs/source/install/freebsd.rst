=====================================
Préparer l'environnement sous FreeBSD
=====================================

A propos
========

Documentation écrite lors du déploiement de la maquette (orientée démo clientes) sur une dedibox (que nous appelleront familèrement dedicov).

Système d'exploitation freebsd:
::

    $ uname -a
    FreeBSD ecov.makina-corpus.com 6.3-RELEASE-p1 FreeBSD 6.3-RELEASE-p1 #1: Sun Feb 24 23:30:42 CET 2008     root@ecov.makina-corpus.com:/usr/obj/usr/src/sys/DEDIBOX  i386

Utilisation de ports-mgmt/portmanager pour installer les paquets, qui a l'avantage par rapport à ports-mgmt/portupgrade de ne pas avoir ryby en dépendance.

On part sur un serveur apache.

Dépendances
===========

Apache22
--------

Installation d'apache:
::

    # portmanager www/apache22

Options par défaut + MOD_LDAP et MOD_AUTHN_LDAP

Python25
--------

Dépendance de subversion.

Installation de Python25:
::

    # portmanager lang/python2.5

Subversion
----------

Installation de subversion:
::

    # portmanager devel/subversion

Options APACHE2_APR NEON

Remarque : Dépendance Perl installée.

mod_python
----------

Installation de mod_python pour apache:
::

    # portmanager www/mod_python3

Memcached
---------

Installation de memcached:
::

    # portmanager databases/memcached

Installation de la couche de liaison python:
::

    # sudo easy_install-2.5 python-memcached

Remarque: sur minitage on utilisera cmemcache

Simplejson
----------

Dépendance du projet ecov. Installation:
::

    # portmanager devel/py-simplejson

Serveur smtp
------------

Penser à installer un serveur smtp pour pouvoir envoyer des mails d'administration, et pour envoyer des mails avec Django. Sendmail désactivé, postfix installé:
::

    # portmanager mail/postfix23


Installation de GeoDjango
=========================

Référence: `geodjango installation`_

Python25
--------

Installé précédemment : dépendance de subversion.

Geos 3.0.0
----------

Installation de geos 3.0.0:
::

    # portmanager graphics/geos

Version 3.0.0 dans les ports.

Proj 4.6.0
----------

Installation de proj 4.6.0:
::

    # portmanager graphics/proj

Version 4.6.0 dans les ports.

Postgres 8.3
------------

Installation de prostgres 8.3 client et server (client dépendance de server):
::

    # portmanager postgresql83-server

Options NLS OPTIMIZED_CFLAGS INTDATE XML TZDATA

Postgis 1.3.2
-------------

Installation de postgis 1.3.2:
::

    # portmanager databases/postgis

Option "GEOS UTF8"

Version 1.3.2 dans les ports.

Gdal 1.5.0
----------

Installation de gdal 1.5.0:
::

    # echo "graphics/gdal|NOPORTDOCS=1|" >> /usr/local/etc/portmanager/pm-020.conf
    # portmanager graphics/gdal

Options GEOS PROJ4

Version 1.5.0 dans les ports.

Psycopg 2.0.6
--------------

Installation de psycopg 2.0.6:
::

    # portmanager databases/py-psycopg2

Version 2.0.6 dans les ports.

Django
------

A ne pas checkouter, les sources sont dans un svn:externals dans la repository ecov.

Démarrer les services
=====================

Vérifier la config des scripts rc.d:
::

    # vim /etc/rc.conf

Postgres
--------

Premier démarrage:
::

    # echo postgresql_enable="YES" >> /etc/rc.conf
    # echo postgresql_data="/var/pgsql/data" >> /etc/rc.conf
    # mkdir /var/pgsql
    # chown pgsql:pgsql /var/pgsql
    # pw usermod pgsql -d /var/pgsql
    # rm -rf /usr/local/pgsql
    # chmod 700 /var/pgsql
    # /usr/local/etc/rc.d/postgresql initdb

Editer /var/pgsql/data/pg_hba.conf et remplacer la fin par:
::

    local   all         pgsql                             ident sameuser
    local   all         all                               md5
    host    all         all         127.0.0.1/32          md5
    host    all         all         ::1/128               md5


Démarrer postgres:
::

    # /usr/local/etc/rc.d/postgresql start

Apache
------

Premier démarrage:
::

    # echo apache22_enable="YES" >> /etc/rc.conf
    # /usr/local/etc/rc.d/apache22 start

Memcached
---------

Premier démarrage:
::

    # echo memcached_enable="YES" >> /etc/rc.conf
    # /usr/local/etc/rc.d/memcached start

Déploiement d'ecov
==================

Architecture
------------

On crée l'architecture suivante:
::

    /var
      makina
        ecov
          application
          cache
            eggs
          conf
          logs

+ application: on y checkoute le projet ecov
+ conf: contient la config apache
+ cache: pour les cache eggs (cf config apache)
+ eggs: faire un chown www dessus
+ logs: contient les logs de l'application

Checkout d'ecov
---------------

Déployé sur dedicov: r564 (23/04/2008)

Penser à éditer son $HOME/.subversion/config pour désactiver l'enregistrement
de son mot de passe LDAP lors d'un svn checkout ou update:
::

    store-passwords = no
    store-auth-creds = no

Checkout d'ecov:
::

    # cd /var/makina/ecov
    # svn co -r<rev> https://subversion.makina-corpus.net/bisonvert/trunk application

Django est en svn:externals dans le dossier /var/makina/ecov/application/lib/django.

Tester gdal
-----------

::

    $ python
    Python 2.5.2 (r252:60911, Feb 25 2008, 00:00:36) 
    [GCC 3.4.6 [FreeBSD] 20060305] on freebsd6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from django.contrib.gis.gdal import HAS_GDAL
    >>> print HAS_GDAL # Will be False if GDAL libraries are not found
    True
    >>> from django.contrib.gis.tests import test_gdal
    >>> test_gdal.run()
    .......................
    BEGIN - expecting IllegalArgumentException; safe to ignore.
    ERROR 1: IllegalArgumentException: points must form a closed linestring
    END - expecting IllegalArgumentException; safe to ignore.
    ......................
    ----------------------------------------------------------------------
    Ran 45 tests in 0.434s
    OK

Tester geos
-----------

::

    $ python
    Python 2.5.2 (r252:60911, Feb 25 2008, 00:00:36) 
    [GCC 3.4.6 [FreeBSD] 20060305] on freebsd6
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from django.contrib.gis.tests import test_geos
    >>> test_geos.run()
    Testing WKT output. ... ok
    Testing HEX output. ... ok
    Testing KML output. ... ok
    Testing the Error handlers. ... 
    BEGIN - expecting GEOS_ERROR; safe to ignore.
    GEOS_ERROR: ParseException: Expected number but encountered ','
    GEOS_ERROR: ParseException: Unknown WKB type 255
    END - expecting GEOS_ERROR; safe to ignore.
    GEOS_ERROR: ParseException: Unexpected EOF parsing WKB
    ok
    Testing WKB output. ... ok
    Testing creation from HEX. ... ok
    Testing creation from WKB. ... ok
    Testing EWKT. ... ok
    Testing GeoJSON input/output (via GDAL). ... ok
    Testing equivalence with WKT. ... ok
    Testing Point objects. ... ok
    Testing MultiPoint objects. ... ok
    Testing LineString objects. ... ok
    Testing MultiLineString objects. ... ok
    Testing LinearRing objects. ... ok
    Testing Polygon objects. ... ok
    Testing MultiPolygon objects. ... 
    BEGIN - expecting GEOS_NOTICE; safe to ignore.
    GEOS_NOTICE: Duplicate Rings at or near point 60 300
    END - expecting GEOS_NOTICE; safe to ignore.
    ok
    Testing Geometry __del__() on rings and polygons. ... ok
    Testing Coordinate Sequence objects. ... ok
    Testing relate() and relate_pattern(). ... ok
    Testing intersects() and intersection(). ... ok
    Testing union(). ... ok
    Testing difference(). ... ok
    Testing sym_difference(). ... ok
    Testing buffer(). ... ok
    Testing the SRID property and keyword. ... ok
    Testing the mutability of Polygons and Geometry Collections. ... ok
    Testing three-dimensional geometries. ... ok
    Testing the distance() function. ... ok
    Testing the length property. ... ok
    Testing empty geometries and collections. ... ok
    Testing `ogr` and `srs` properties. ... ok
    Testing use with the Python `copy` module. ... ok
    Testing `transform` method. ... ok
    Testing `extent` method. ... ok
    ----------------------------------------------------------------------
    Ran 35 tests in 0.670s
    OK


Config du serveur web
======================

Config apache
-------------

Config apache dans le fichier /var/makina/ecov/conf/apache22.conf: voir les
fichiers https://subversion.makina-corpus.net/bisonvert/conf/apache22.conf.dedibox et https://subversion.makina-corpus.net/bisonvert/conf/apache22-dev.conf.dedibox

A noter: auth LDAP + htpasswd

Lien symbolique vers ce fichier dans /usr/local/etc/apache22/Includes/

Dans le fichier /usr/local/etc/apache22/httdp.conf, on rajoute pour l'auth LDAP:
::

    <IfModule ldap_module>
    LDAPSharedCacheSize 200000
    LDAPCacheEntries 1024
    LDAPCacheTTL 600
    LDAPOpCacheEntries 1024
    LDAPOpCacheTTL 600
    </IfModule>

Ajouter un accès htpassword
---------------------------

Les mots de passe sont stockés dans /var/makina/ecov/conf/htpassword.

Pour ajouter un accès, faire:
::

    # cd /var/makina/ecov/conf
    # htpasswd htpasswd <username>
    New password:
    Re-type new password:
    Adding password for user <username>


.. _`geodjango installation`: http://code.djangoproject.com/wiki/GeoDjangoInstall#GeoDjangoInstallation
