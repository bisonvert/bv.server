===================================
Installation complète en production
===================================

A propos
========

Documentation écrite lors du déploiement de la production sur serveur PHPNET dédié Intel Core2Duo E6400/2G RAM.

Système d'exploitation Debian stable 4:
::

    $ uname -a
    Linux phpnetd059 2.6.18-6-686 #1 SMP Sun Feb 10 22:11:31 UTC 2008 i686 GNU/Linux


Modification Base subversion
============================

Attention, par rapport au reste de ce document la base subversion en production a été modifiee pour se servir d'une branche particuliere.
Il n'y a donc plus de reference au trunk en production. La doc originale commence a 'Installation' et a ete faite avant ce changement.

Description du changement: Changement de la branche Trunk à une branche de production:
--------------------------------------------------------------------------------------

Au niveau de la gestion des sources dans le subversion:
::

    /trunk (...dev...)
    /tags
    /branches
      buildout  (utilisation du buildout sur le trunk
      bisonvert.v1.0.beta (première branche de production)
      production (copie de la branche buildout mais fonctionnant sur bisonvert.v1.0.beta)

On a donc recopié le EXTERNALS.txt de buildout dans production, en remplacant les https://subversion.makina-corpus.net/bisonvert/trunk/(...) par https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta/(...)

Puis on modifie les propriétés svn (propset) external de ce projet afin qu'elles correspondent à ce fichier external.
svn propedit svn:externals .
::

    hooks https://subversion.makina-corpus.net/zopina/buildouts/hooks/branches/meta
    shell https://subversion.makina-corpus.net/zopina/buildouts/shell/trunk
    templates https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta/templates
    ecov https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta/ecov
    share https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta/share
    media https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta/media

Sur le serveur de production qui possède une version du trunk on va devoir relocaliser le source (svn switch):
::

    # cd /var/makina/bisonvert/minitage/django/bisonvert
    # ls -lh
    total 28K
    drwxr-sr-x 9 root zope 4,0K 2008-03-28 18:42 ecov
    -rw-r--r-- 1 root zope  418 2008-03-28 12:04 EXTERNALS.txt
    drwxr-sr-x 3 zope zope 4,0K 2008-03-28 11:19 hooks
    drwxr-sr-x 7 root zope 4,0K 2008-03-28 12:04 media
    drwxr-sr-x 6 root zope 4,0K 2008-03-28 12:04 share
    drwxr-sr-x 3 zope zope 4,0K 2008-03-28 16:34 shell
    drwxr-sr-x 7 root zope 4,0K 2008-03-28 12:04 templates
    # svn info|grep URL
    URL : https://subversion.makina-corpus.net/bisonvert/branches/buildout
    # svn switch https://subversion.makina-corpus.net/bisonvert/branches/production/ .

On doit voir:
::

    U    EXTERNALS.txt
    U (...)



Installation
============

On part sur un serveur apache.

Apache22
--------

Installation d'apache::

 # apt-get install apache2-mpm-prefork apache2-utils apache2.2-common libapache2-mod-python
 # jouer avec a2enmod jusqua obtention de:
 phpnetd059:~# apache2 -t -D DUMP_MODULES
 Loaded Modules:
  core_module (static)
  log_config_module (static)
  logio_module (static)
  mpm_prefork_module (static)
  http_module (static)
  so_module (static)
  alias_module (shared)
  auth_basic_module (shared)
  authn_file_module (shared)
  authnz_ldap_module (shared)
  authz_default_module (shared)
  authz_groupfile_module (shared)
  authz_host_module (shared)
  authz_user_module (shared)
  cache_module (shared)
  cgi_module (shared)
  deflate_module (shared)
  dir_module (shared)
  env_module (shared)
  expires_module (shared)
  filter_module (shared)
  headers_module (shared)
  ldap_module (shared)
  mime_module (shared)
  mime_magic_module (shared)
  python_module (shared)
  proxy_module (shared)
  rewrite_module (shared)
  setenvif_module (shared)
  ssl_module (shared)
  status_module (shared)

 #apt-get install cronolog

Configuration VHost Apache
..........................

::

    # cd /var/makina/bisonvert
    # svn co https://subversion.makina-corpus.net/bisonvert/conf conf
    # ln -s /var/makina/bisonvert/conf/apache.conf.production /etc/apache2/sites-available/50-www.bisonvert.net
    # a2ensite 50-www.bisonvert.net

Installation du projet avec minitage, deployeur automatique
-----------------------------------------------------------

::

    # adduser zope
    # apt-get install build-essential
    # mkdir -p /var/makina/bisonvert/ 
    # chown rle:zope /var/makina/bisonvert/
    # chmod 2775 /var/makina/bisonvert/

On passe en session zope:
::

    # su - zope
    # mkdir -p ~/.buildout/downloads
    # cat << EOF > ~/.buildout/default.cfg
    [buildout]
    download-directory = $HOME/.buildout/downloads
    download-cache = $HOME/.buildout/downloads
    EOF

    # export mt=/var/makina/bisonvert/minitage
    # export mypy=/home/zope/tools/python2.4
    # mkdir -p $mt
    # svn co https://subversion.makina-corpus.net/zopina/buildouts/minitage/trunk/ $mt
    # cd $mt
    # mkdir -p $mypy
    # shell/MakinaBootstrapper.sh $mypy

Installation virtualenv:
::

    # $mypy/bin/virtualenv $mt

aller chercher packets minitages de ce projet:
::

    # svn co https://subversion.makina-corpus.net/bisonvert/minilays/trunk/ $mt/minilays/bisonvert
    # cat /var/makina/bisonvert/minitage/minilays/bisonvert/meta-bisonvert
    gdal-1.5 prepends all the other dependencies right now (minitageV3)!
    local libs="gdal-1.5"
    local eggs="egg-xml simplejson-1.0.1 psycopg2-2.0.6 geodjango-r7283"
    local instances="bisonvert"
    depends=" $libs $eggs $instances"
    $ cat /var/makina/bisonvert/minitage/minilays/bisonvert/bisonvert
    install_method="buildout"
    src_uri="https://subversion.makina-corpus.net/bisonvert/branches/buildout/"
    src_type="svn"
    category="django"

installer bisonvert:
::

     # cd $mt
     # ./minimerge meta-bisonvert

Qui devrait donner quelque chose du genre:
::

    >>> Testing for VirtualEnv presence
    * VirtualEnv activated in .
    ./lib/minitage/functions.sh: line 97: openssl-0.9: Aucun fichier ou répertoire de ce type
    >>> Will now fetch/merge:  ./minilays/dependencies/bzip2-1.0 ./minilays/dependencies/zlib-1.2 ./minilays/dependencies/openssl-0.9 ./minilays/dependencies/ncurses-5.6 ./minilays/dependencies/readline-5.2 ./minilays/dependencies/db-4.4 ./minilays/dependencies/expat-2.0 ./minilays/dependencies/python-2.5 ./minilays/dependencies/libiconv-1.12 ./minilays/dependencies/libjpeg-6b ./minilays/dependencies/libtiff-3.8 ./minilays/dependencies/libpng-1.2 ./minilays/dependencies/libgif-1.4 ./minilays/meta/meta-imaging-libs ./minilays/dependencies/python-2.4 ./minilays/dependencies/libxml2-2.6 ./minilays/dependencies/libxslt-1.1 ./minilays/meta/meta-xml ./minilays/dependencies/freetype-2.1 ./minilays/dependencies/fontconfig-2.5 ./minilays/dependencies/libgd-2.0 ./minilays/dependencies/swig-1.3 ./minilays/dependencies/flex-2.5 ./minilays/dependencies/cyrus-sasl-2.1 ./minilays/dependencies/openldap-2.3 ./minilays/dependencies/postgresql-8.2-py2.5 ./minilays/dependencies/proj-4.5 ./minilays/dependencies/geos-3.0 ./minilays/dependencies/postgis-1.2-py2.5 ./minilays/dependencies/curl-7.16 ./minilays/dependencies/gdal-1.5 ./minilays/dependencies/python ./minilays/eggs/elementtree-1.2.7_20070827_preview ./minilays/eggs/lxml-2.0beta1 ./minilays/eggs/egg-xml ./minilays/eggs/simplejson-1.0.1 ./minilays/dependencies/postgresql-8.2 ./minilays/eggs/psycopg2-2.0.6 ./minilays/eggs/geodjango-r7283 ./minilays/bisonvert/bisonvert ./minilays/bisonvert/meta-bisonvert
    * Merging ./minilays/dependencies/bzip2-1.0
    >>> Fething svn ::> https://subversion.makina-corpus.net/zopina/buildouts/buildout-meta/trunk/ultimate-dependencies/bzip2-1.0.4/
    * Trying to get from "https://subversion.makina-corpus.net/zopina/buildouts/buildout-meta/trunk/ultimate-dependencies/bzip2-1.0.4/" to "./dependencies/bzip2-1.0" with "co" as svn args
    ...

#HACK : pour forcer postgis a la version 1.3.2 au lieu de 1.2.1 comme dans le zopina actuel j'ai modifie:
::

    minitage/minilays/dependencies/gdal-1.5 a la ligne  :
    depends='python-2.5 libiconv-1.12 meta-imaging-libs libgd-2.0 swig-1.3 flex-2.5 postgis-1.3-py2.5 proj-4.5 geos-3.0 curl-7.16'
    afin qu'il se serve d'un postgis-1.3-py2.5 que j'ai cree. Il faudra voir a commiter cette dependance de facon plus propre

# le python à utiliser pour django est:
::

    $mt/django/bisonvert/shell/geodjango-r7283.python

soit : /var/makina/bisonvert/minitage/django/bisonvert/shell/geodjango-r7283.python

On l'enregistre dans /etc/profile en PROD_PYTHON:
::

    PROD_PYTHON="/var/makina/bisonvert/minitage/django/bisonvert/shell/geodjango-r7283.python"
    export PROD_PYTHON

Test de gdal:
::

    $ /var/makina/bisonvert/minitage/django/bisonvert/shell/geodjango-r7283.python
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

Test de geos:
::

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


Finitions
----------

Subversion
..........

Installation de subversion::
    # apt-get install subversion

Serveur smtp
............

Penser à installer un serveur smtp pour pouvoir envoyer des mails d'administration, et pour envoyer des mails avec Django. Sendmail désactivé, postfix installé::

    # apt-get install postfix

TODO: autoriser relai dans postfix makina central


Postgres 8.2 (dev 8.3)
......................

Installation de prostgres 8.2 client et server (client dépendance de server)::
On sert sert d'un backport pour etch
::

    # ajouter a /etc/apt/source.list:
    #    deb http://www.backports.org/debian etch-backports main contrib non-free
    # apt-get update
    # apt-get install debian-backports-keyring
    # apt-get update
    # apt-get install postgresql-7.4
    # apt-get install -t etch-backports postgresql-8.2 
    # /etc/init.d/postgresql-7.4 stop
    # /etc/init.d/postgresql-8.2 stop
    # chown postgres /var/log/postgresql

Faire tourner le bon postgres
-----------------------------

On va bidouiller le postgresql debian pour charger le notre, celui du bouildout
::

    su - postgres
    /var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/part/bin/initdb /var/lib/postgresql/8.2/main
    cp /var/lib/postgresql/8.2/oldmain/postmaster.opts /var/lib/postgresql/8.2/main
    rm /var/lib/postgresql/8.2/main/postgresql.conf
    vi /var/lib/postgresql/8.2/main/postmaster.opts   -------------------
    /var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/part/bin/postgres -D /var/lib/postgresql/8.2/main -c config_file=/etc/postgresql/8.2/main/postgresql.conf

    vi /usr/share/postgresql-common/PgCommon.pm -------------------
    my $binroot = "/var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/";
    #my $binroot = "/usr/lib/postgresql";

    ln -s  /var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/part/ /var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/8.2 


Recopier les fichiers de conf présents dans le subversion (/conf) ou bien editer a la main:

Editer /etc/postgresql/8.2/main/pg_hba.conf on doit avoir:
::

    # Database administrative login by UNIX sockets
    local   all         postgres                          ident sameuser

    # TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD

    # "local" is for Unix domain socket connections only
    local   bisonvert   bzonvert                          md5
    local   all         all                               ident sameuser
    # IPv4 local connections:
    host    all         all         127.0.0.1/32          md5
    # IPv6 local connections:
    host    all         all         ::1/128               md5
    --------------------------------------------------------------------

Editer /etc/postgresql/8.2/main/postgresql.conf, on doit avoir:
::

    . listen_addresses = 'localhost'
    . max_connections = 1000 
    . superuser_reserved_connections = 3
    . ssl = off
    . shared_buffers = 64MB
    . temp_buffers = 4096
    . max_prepared_transactions = 25
    . work_mem = 4096KB
    . maintenance_work_mem = 16384KB
    . max_stack_depth = 4096KB
    . max_fsm_pages = 153600
    . log_destination = 'stderr'
    . redirect_stderr = on
    . log_directory = '/var/log/postgresql'
    . log_rotation_size = 10MB
    . client_min_messages = warning
    . log_min_messages = warning
    . log_min_error_statement = error
    . stats_row_level = on
    . stats_start_collector = on
    . autovacuum = on
    . autovacuum_naptime = 1min
    . autovacuum_vacuum_threshold = 1000
    . autovacuum_analyze_threshold = 500
    . autovacuum_vacuum_scale_factor = 0.4
    . autovacuum_analyze_scale_factor = 0.2
    . autovacuum_vacuum_cost_delay = -1 
    . autovacuum_vacuum_cost_limit = -1

::

    #  chown postgres /var/log/postgresql/
    # vi /etc/sysctl.conf ----------
    # SHARED BUFFERS --> necessary for postgresql shred_buffers allocation
    #  previously was:
    #  shmmax  33554432
    #  shmall  2097152
    kernel.shmall = 134217728
    kernel.shmmax = 134217728
    --------------------------
    # sysctl -p

Démarrer postgres:
::

    # /etc/init.d/postgresql start


Déploiement de bison vert
=========================

Création de la BDD
------------------

Création de la BDD:
::

    # su - postgres
    $ createuser -P bzonvert
    Enter password for new role: -> see FichierSecret Makina
    Enter it again:
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n
    $ /var/makina/bisonvert/minitage/dependencies/postgresql-8.2-py2.5/part/bin/createdb -O bzonvert -E utf8  bisonvert
    $ createlang plpgsql bisonvert
    $ psql -d bisonvert -f /var/makina/bisonvert/minitage/dependencies/postgis-1.3-py2.5/part/share/lwpostgis.sql
    $ psql -d bisonvert -f /var/makina/bisonvert/minitage/dependencies/postgis-1.3-py2.5/part/share/spatial_ref_sys.sql
    $ psql bisonvert
    bisonvert=# GRANT SELECT, UPDATE, INSERT, DELETE ON geometry_columns TO "bzonvert";
    bisonvert=# GRANT SELECT ON spatial_ref_sys TO "bzonvert";
    verification avec \dp
               Privilèges d'accès pour la base de données « bisonvert »
    Schéma |       Nom        | Type  |                Privilèges d'accès
    --------+------------------+-------+---------------------------------------------------
    public | geometry_columns | table | {postgres=arwdxt/postgres,bzonvert=arwd/postgres}
    public | spatial_ref_sys  | table | {postgres=arwdxt/postgres,bzonvert=r/postgres}
    (2 lignes)


Architecture
------------

on crée l'architecture suivante::

 /var
   makina
    bisonvert
      minitage
      cache
        eggs
      conf
      logs

+ minitage on y construit TOUT
+ conf: contient la config apache
+ cache: pour les cache eggs (cf config apache)
+ eggs: faire un chown www dessus
+ logs: contient les logs de l'application

le repertoire principal de l'application devient:
::

    /var/makina/bisonvert/minitage/django/bisonvert

On le met dans le /etc/profile en tant que $PROD_APP:
::

    --- /etc/profile --------
    PROD_APP="/var/makina/bisonvert/minitage/django/bisonvert/"
    export PROD_APP
    -------------------------

ATTENTION
---------

Penser à éditer son $HOME/.subversion/config pour activer:
::

    store-passwords = no
    store-auth-creds = no

et a virer les $HOME/.subversion/auth/svn.simple/\*, le tout APRES le minitage de preference!!

Paramétrage de settings.py
--------------------------

On utilise le fichier de configuration qui va bien dans le répertoire
ecov/conf/


Installation du modèle
----------------------

cf :ref:`install-install_bv-model-label` et :ref:`install-install_bv-sql-label`

Correction du mod_python
------------------------

Si on installle libapache2-mod-python sur Debian on obtient les fichiers qu'il faut pour intégrer facilement mod_pythopn dans apache
SAUF QUE c'est python2.4 qui sera pris au lieu de notre petit python à nous.
Il faut donc recompiler mod_python.
::

    # apt-get install apache2-prefork-dev
    # cd /usr/local/src/
    # wget http://apache.cict.fr/httpd/modpython/mod_python-3.3.1.tgz
    # tar xfvz mod_python-3.3.1.tgz
    # cd mod_python-3.3.1
    # export CFLAGS="-I/var/makina/bisonvert/minitage/dependencies/python-2.5/part/include"
    # export LDFLAGS="-L/var/makina/bisonvert/minitage/dependencies/python-2.5/part/lib -Wl,-rpath -Wl,/var/makina/bisonvert/minitage/dependencies/python-2.5/part/lib"
    # ./configure --with-python=/var/makina/bisonvert/minitage/dependencies/python-2.5/part/bin/python2.5
    # make
    # make install
    # /etc/init.d/apache2 force-reload

Correction gestion python dans Apache
-------------------------------------

::

    # chown zope:www-data /var/makina/bisonvert/cache/eggs
    # chmod 2775 /var/makina/bisonvert/cache/eggs

Pour une bonne gestion de python et de nos libs specifiques dans mod_python on va devoir faire deux trois petites choses:
::

    # mkdir /var/makina/bisonvert/bin
    # ln -s $PROD_PYTHON /var/makina/bisonvert/bin/python

Dans /etc/init.d/apache2 tout en haut:
::

    ENV="env -i LANG=C PATH=/var/makina/bisonvert/bin:/usr/local/bin:/usr/bin:/bin LD_LIBRARY_PATH=var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/geos-3.0/part/lib:/var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/gdal-1.5/part/lib:/var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/postgis-1.2-py2.5/part/lib:/var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/postgresql-8.2-py2.5/part/lib:/var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/proj-4.5/part/lib:/var/makina/bisonvert/minitage/django/bisonvert/shell/../../..//dependencies/python-2.5/part/lib GDAL_DATA=/var/makina/bisonvert/minitage/django/bisonvert/dependencies/gdal-1.5/part/share/"

Et les SetEnv dans la conf virtualHost (voir la conf dans le subversion bisonvert/conf/apache*
