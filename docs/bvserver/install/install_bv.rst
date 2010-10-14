.. _install-install_bv-label:

================================================
Déployer BisonVert une fois l'environnement prêt
================================================

Une fois l'environnement prêt, il faut:

+ créer la base de données
+ paramétrer un fichier de configuration (settings.py)
+ installer le modèle django de BisonVert
+ importer les procédures, les triggers et créer les colonnes additionnelles

Création de la BDD
==================

La bdd est déjà créée (créée lors de la crétaion du profil pg).

Installer les script PostGIS et pgRouting:
::


.. XXX
.. bisonvert.psql  -U djcoin < ../../dependencies/postgresql-8.4/parts/part/share/contrib/postgis.sql 
.. bisonvert.psql  -U djcoin < ../../dependencies/postgresql-8.4/parts/part/share/contrib/spatial_ref_sys.sql 

    bv.createlang plpgsql bv
    bv.psql -f $mt/dependencies/postgis-1.3/parts/part/share/lwpostgis.sql
    bv.psql -f $mt/dependencies/postgis-1.3/parts/part/share/spatial_ref_sys.sql

Si le vous décidez de modifier le owner de la bdd, et donc de ne plus utiliser le superuser, ne pas oublier:
::

    bv.psql
    bv=# GRANT SELECT, UPDATE, INSERT, DELETE ON geometry_columns TO <db_user>;
    bv=# GRANT SELECT ON spatial_ref_sys TO <db_user>;

.. _install-install_bv-settings-label:

Paramétrage de settings.py
==========================

.. XXX
.. le fichier ne s'appelle plus comme ca ...
.. /home/djcoin/minitage/django/bv.server/etc/django-settings/settings-BOX-dev.py:1
.. wrong : piston not found ..

Le fichier ecov.settings.py qui est sous svn est un exemple de
fichier de configuration pour le projet BisonVert. Il contient tous les
paramètres indispensables au bon fonctionnement de l'application.

BisonVert est appelé à être déployé sur plusieurs serveurs, le plus souvent en
mode mutualisé: l'application est déployée une seule et unique fois, mais
plusieurs fichiers de configuration seront utilisés, un par vhost.

La procédure est la suivante:

+ On ne modifie jamais le fichier ecov.settings.py, sauf pendant la phase de
  développement, pour rajouter/modifier/supprimer des paramètres
+ Sur nos environnements de développement, on crée un fichier (par exemple
  settings_local.py) dans le répertoire ecov/conf/ sur le modèle suivant:
  ::

    # -*- coding: utf-8 -*-
    # vim: set fileencoding=utf-8 :

    import os.path

    ##########################################################
    # Variables to set first

    DEBUG = True
    PROJECT_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')

    ##########################################################
    # Loading default settings

    try:
        path = "../settings.py"
        path = os.path.join(os.path.dirname(__file__), path)
        execfile(path)
    except ImportError, e:
        import sys
        sys.stderr.write("Unable to read settings.py\n")
        sys.exit(1)

    ##########################################################
    # Specific settings

    PROJECT_ROOT_URL = 'http://url/to/project:port'

    # For SQL Query logger
    SQL_LOG_PATHFILE = '/path/to/sql.log'
    SQL_LOG = False
    
    # Path to log for cron scripts
    SCRIPTS_LOG_PATH = "/path/to/logs/cron"
    SCRIPTS_LOG_PREFIX = "instancename"

    # Google Maps
    GOOGLE_MAPS_API_KEY = '<clé google maps en accord avec le vhost utilisé>'

    ADMINS = ( # DEFAULT
        ('Admin Name', 'admin@foo.bar'),
    )
    # for admin messages
    EMAIL_SUBJECT_PREFIX = '[Django] '
    SERVER_EMAIL = 'admin@foo.bar'

    # Emails
    FROM_EMAIL = 'admin@foo.bar'
    CONTACT_EMAIL = 'admin@foo.bar'

    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = '<db_name>'             # Or path to database file if using sqlite3.
    DATABASE_USER = '<db_user>'             # Not used with sqlite3.
    DATABASE_PASSWORD = '<db_pwd>'         # Not used with sqlite3.
    DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = '<db_port>'             # Set to empty string for default. Not used with sqlite3.

    EMAIL_HOST = '127.0.0.1'
    EMAIL_HOST_PASSWORD = ''
    EMAIL_HOST_USER = ''
    EMAIL_PORT = 25
    EMAIL_USE_TLS = False

+ Tout paramètre qui doit être modifié pour des besoins particuliers liés à une
  machine (modification d'une URL, des paramètres de connexion à la BDD, etc)
  doit être écrit dans ce fichier
+ Tout fichier de configuration écrit pour une prod (ou une maquette) est mise
  en conf dans le répertoire ecov/conf

.. note::

    Les paramètres qui sont notés DEFAULT dans le fichier ecov.settings.py sont
    susceptibles d'être modifiés. Les autres paramètres sont globaux à toutes
    les installations.


En production (ou sur les maquettes de démo clientes), pour éviter les problèmes de cache côté navigateur pour les fichiers statiques, on paramètre le /media comme ceci:
::

    # une_date au format YYYYMMDD
    MEDIA_URL = '/media/<une_date>/'

.. _install-install_bv-model-label:

Installation du modèle
======================

Pour toute utilisation du script bv_manage, penser à positionner le bon
fichier de configuration.

Installation du modèle de données ecov:
::

.. XXX -> nop deal with the setting of bv.server

    cd $mt/django/eco-mobile-dev/src/eco-mobile/src
    bv_manage syncdb --settings=ecov.conf.<SETTINGS_FILE>

Créer un admin (demandé par Django lors du syncdb):
::

    You just installed Django's auth system, which means you don't have any superusers defined.
    Would you like to create one now? (yes/no): yes
    ...

.. _install-install_bv-sql-label:

Importer les fichiers SQL propres au projet
===========================================

::

    cd $mt/django/bisonvert-dev/src/bisonvert/src

.. XXX changer partout bisonvert-dev par bv.server
.. cd $mt/django/bv.server/ # les *sql sont la

Importer les procédures perso dans la BDD:
::

    bv.psql -f share/data/procedures.sql

Importer les triggers perso dans la BDD:
::

    bv.psql -f share/data/trigger.sql

Créer les champs non modélisés:
::

    bv.psql -f share/data/additional_columns.sql

.. XXX: require -U <superuser>

Définition des tâches périodiques
=================================

Certains scripts de l'application Bisonvert ont besoin d'être lancés périodiquement via des scripts cron.
Il s'agit notamment de:

+ ecov/site/scripts - run_alert()
+ ecov/rating/scripts - run_alert()
+ ecov/rating/scripts - run_purge()

Il faut lancer ces scripts toutes les 24 heures, pour le moment l'heure a été choisie de façon arbitraire.
Le lancement de ces scripts python passe par l'intermédiaire de scripts shell pour éviter de surcharger le fichier de crontab.


.. XXX ils ne sont pas valables pour des versions de developement...
Arborescence des scripts shell:
::

    $mt/django/bisonvert/share/conf/shell/XXX/*.sh

Il faut adapter les cron en fonction de la machine sur laquelle la configuration est effectuée.

Exemple:
::

    "sudo contrab -e"
    # m h  dom mon dow   command
    00 02 * * * /var/www/ecov_svn/share/conf/shell/xenecov/site_run_alert_cron.sh

Répertoire "xenecov" pour la version de développement sur le xen de makina Nantes, pour lancer le script d'alertes mail.

Le sudo est nécessaire pour lancer ce crontab en tant qu'utilisateur root **sur le xen uniquement** (projet checkouté avec un sudo) - en prod on travaille avec le user zope.
