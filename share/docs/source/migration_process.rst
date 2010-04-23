=========
Migration
=========

Cette page décrit les étapes du déploiement de chaque version du projet BisonVert, du plus récent au plus ancien.

Elle est orientée production, donc doit être adaptée pour une migration sur une autre plateforme.


Migration Tag bisonvert.v1.1.beta.7 -> Tag bisonvert.v1.1.beta.8
================================================================

Déploiement prévu le jeudi 14/05/2009.

cf :ref:`svn_layout-svn_history-br1.1.beta-label` pour voir les modifications effectuées.

Apache - Pages de maintenance
-----------------------------

Mettre les pages de maintenance à jour:
::

    cd /var/makina/bv/maintenance
    svn up

Activer les pages de maintenance:
::

    cd /etc/apache2/sites-available
    sudo rm 50-www.bisonvert.net-maintenance 51-www2.bisonvert.net-maintenance
    sudo ln -s /var/makina/bv/maintenance/conf/apache/phpnet1/bisonvert 50-bisonvert-maintenance
    sudo a2dissite 50-www.bisonvert.net
    sudo a2dissite 51-www2.bisonvert.net
    sudo a2ensite 50-bisonvert-maintenance
    sudo /etc/init.d/apache2 reload

Stopper spawning:
::

    sudo /etc/init.d/paste_bisonvert.prod stop

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    export mt=/var/makina/bv/minitage/

minimerge:
::

    cd $mt
    source bin/activate
    minimerge -NUuR bisonvert

Système
.......

N/A

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Apache - remise en prod
-----------------------

Starter spawning:
::

    sudo /etc/init.d/paste_bisonvert.prod start


Rétablir les vhosts:
::

    cd /etc/apache2/sites-available
    sudo a2dissite 50-bisonvert-maintenance
    sudo a2ensite 50-www.bisonvert.net
    sudo a2ensite 51-www2.bisonvert.net
    sudo /etc/init.d/apache2 reload

Migration Tag bisonvert.v1.1.beta.6 -> Tag bisonvert.v1.1.beta.7
================================================================

Déploiement terminé le lundi 11/05/2009.

Passage à minitage 1.0.

+ rep /var/makina/bv/minitage
+ user dbbv
+ minimerge bisonvert
+ paster pg
+ paster dj.paste
+ scripts d'init pg et paste dans /etc/init.d/
+ install scripts cron
+ config apache: 50-www.bisonvert.net et 51-www2.bisonvert.net

Récupération de l'ancienne base via dumpdata, puis loaddata.

Migration Tag bisonvert.v1.1.beta.5 -> Tag bisonvert.v1.1.beta.6
================================================================

Déploiement le mercredi 03/09/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.6/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.6/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

N/A

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance



Migration Tag bisonvert.v1.1.beta.4 -> Tag bisonvert.v1.1.beta.5
================================================================

Déploiement le vendredi 29/08/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.5/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.5/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

N/A

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance



Migration Tag bisonvert.v1.1.beta.3 -> Tag bisonvert.v1.1.beta.4
================================================================

Déploiement le vendredi 11/07/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.4/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.4/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

N/A

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance



Migration Tag bisonvert.v1.1.beta.2 -> Tag bisonvert.v1.1.beta.3
================================================================

Déploiement le mardi 01/07/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.3/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.3/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

N/A

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance



Migration Tag bisonvert.v1.1.beta.1 -> Tag bisonvert.v1.1.beta.2
================================================================

Déploiement le vendredi 20/06/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.2/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.2/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

Hack pour éviter les pb de cache des fichiers compilés avec mod_python:
::

    $ cd $mt/django/bisonvert/shell
    $ ln -s django.python django.www2.python

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance



Migration Tag bisonvert.v1.1.beta.0 -> Tag bisonvert.v1.1.beta.1
================================================================

Déploiement le vendredi 06/06/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.1/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.1/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

Hack pour éviter les pb de cache des fichiers compilés avec mod_python:
::

    $ cd $mt/django/bisonvert/shell
    $ ln -s django.python django.www2.python

Procédure de migration
----------------------

Modifications SQL
.................

N/A

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance


Migration Tag bisonvert.v1.0.beta-1.1 -> Tag bisonvert.v1.1.beta.0
==================================================================

Déploiement le lundi 02/06/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.0/maintenance
    
Vérifier que les liens symboliques du dossier ``/etc/apache2/sites-available/`` pointent vers les fichiers de maintenance (dans le dossier ``/var/makina/bisonvert/maintenance/conf/apache/phpnet1/``).

Activer la page de maintenance pour les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net
    $ a2ensite 50-www.bisonvert.net-maintenance
    $ a2dissite 51-www2.bisonvert.net
    $ a2ensite 51-www2.bisonvert.net-maintenance
    $ /etc/init.d/apache2 reload

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.1.beta.0/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

Hack pour éviter les pb de cache des fichiers compilés avec mod_python:
::

    $ cd $mt/django/bisonvert/shell
    $ ln -s django.python django.www2.python

Installer les scripts cron qui vont bien, pour le user zope:
::

    # m h  dom mon dow   command
    00 02 * * * /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/site_run_alert_cron.sh
    00 03 * * * /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/rating_run_alert_cron.sh
    00 04 * * * /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/rating_run_purge_cron.sh

Créer le répertoire de logs (il faut que zope puisse y écrire):
::

    $ mkdir -p /var/makina/bisonvert/logs/cron
    
Passer les 3 scripts en exécutables pour le user zope:
::

    $ chmod u+x /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/site_run_alert_cron.sh
    $ chmod u+x /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/rating_run_alert_cron.sh
    $ chmod u+x /var/makina/bisonvert/minitage/django/bisonvert/share/conf/shell/phpnet1/rating_run_purge_cron.sh

Procédure de migration
----------------------

Modifications SQL
.................

Charger le script sql ``share/data/migrations/from_v1.0.beta-1.1_to_v1.1.beta.0/update_before_data_migration.sql``:
::

    $ cd $mt/django/bisonvert
    $ psql -f share/data/migrations/from_v1.0.beta-1.1_to_v1.1.beta.0/update_before_data_migration.sql bisonvert -U bzonvert

Procédures
..........

Charger les procédures:
::

    $ psql -f share/data/procedures.sql bisonvert -U bzonvert

Syncdb
......

Faire un syncdb:
::

    $ ./shell/django.python ecov/manage.py syncdb --settings=ecov.conf.settings_www-bisonvert-net


Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, rétablir les 2 vhosts (en root):
::

    $ a2dissite 50-www.bisonvert.net-maintenance
    $ a2ensite 50-www.bisonvert.net
    $ a2dissite 51-www2.bisonvert.net-maintenance
    $ a2ensite 51-www2.bisonvert.net
    $ /etc/init.d/apache2 reload

Vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance

Migration Tag bisonvert.v1.0.beta-1.0 -> Tag bisonvert.v1.0.beta-1.1
====================================================================

Déploiement le vendredi 09/05/2008.

Sauf mention contraire, travailler avec le user zope.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

Aucune migration du modèle pour ce tag.

Page de maintenance
-------------------

Récupérer les fichiers de maintenance:
::

    $ cd /var/makina/bisonvert
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.0.beta-1.1/maintenance

Linker les confs apache de maintenance (en root):
::

    $ rm /etc/apache2/sites-available/50-www.bisonvert.net
    $ ln -s /var/makina/bisonvert/maintenance/conf/apache/phpnet1/www.bisonvert.net /etc/apache2/sites-available/50-www.bisonvert.net
    $ rm /etc/apache2/sites-available/51-www2.bisonvert.net
    $ ln -s /var/makina/bisonvert/maintenance/conf/apache/phpnet1/www2.bisonvert.net /etc/apache2/sites-available/51-www2.bisonvert.net

Reloader apache, et vérifier que la page de maintenance est bien affichée pour les 2 vhosts.

Mise à jour de l'environnement
------------------------------

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Ménage - Supprimer l'ancien eggs geodjango dont on n'a plus besoin:
::

    $ cd $mt
    $ rm -rf eggs/geodjango-r7283/

Changer le minilay:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.0.beta-1.1/minitage/minilay $mt/minilays/bisonvert

Minimerger le minilay Bisonvert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ ./minimerge -N bisonvert

Système
.......

Hack pour éviter les pb de cache des fichiers compilés avec mod_python:
::

    $ cd $mt/django/bisonvert/shell
    $ ln -s django.python django.www2.python

Procédure de migration
----------------------

N/A

Rétablir l'accès aux site
-------------------------

Linker les bonnes confs apache (en root):
::

    $ rm /etc/apache2/sites-available/50-www.bisonvert.net
    $ ln -s /var/makina/bisonvert/minitage/django/bisonvert/share/conf/apache/phpnet1/www.bisonvert.net /etc/apache2/sites-available/50-www.bisonvert.net
    $ rm /etc/apache2/sites-available/51-www2.bisonvert.net
    $ ln -s /var/makina/bisonvert/minitage/django/bisonvert/share/conf/apache/phpnet1/www2.bisonvert.net /etc/apache2/sites-available/51-www2.bisonvert.net

Reloader apache, et vérifier que le site est accessible pour les 2 vhosts.

Quand c'est bon, faire le ménage:
::

    $ cd /var/makina/bisonvert
    $ rm -rf maintenance

Migration Branche bisonvert.v1.0.beta -> Tag bisonvert.v1.0.beta-1.0
====================================================================

Déploiement le mardi 06/05/2008.

Instances à mettre à jour
-------------------------

PHPNET dédié
............

A ce jour, une seule base à migrer.

+ ``DB_NAME``: bisonvert
+ ``DB_USER``: bzonvert
+ ``SETTINGS_FILE``: ecov.conf.settings_www-bisonvert-net

Page de maintenance
-------------------

Mettre une page de maintenance pour les 2 vhosts.

Mise à jour de l'environnement
------------------------------

Avant toute chose, faire un dump de la bdd, et le stocker bien précieusement dans un coin.
::

    $ pg_dump -F plain -U bzonvert bisonvert -f <OUTPUT_FILENAME>

Pour la suite, sauf mention contraire, travailler avec le user zope.

Minitage
........

::

    $ export mt=/var/makina/bisonvert/minitage/

Commencer par supprimer le minilay ``gdal-1.5`` pour récupérer l'original, et supprimer le minilay ``postgis-1.3-py2.5`` qui n'est pas bon:
::

    $ cd $mt
    $ rm minilays/dependencies/postgis-1.3-py2.5
    $ rm minilays/dependencies/gdal-1.5

Mettre à jour minitage:
::

    $ cd $mt
    $ svn update

On checkoute le bon minilay pour BisonVert:
::

    $ cd $mt
    $ rm -rf minilays/bisonvert/
    $ svn co https://subversion.makina-corpus.net/bisonvert/tags/bisonvert.v1.0.beta-1.0/minitage/minilay/ $mt/minilays/bisonvert

On minimerge le minilay BisonVert:
::

    $ cd $mt
    $ rm -rf django/bisonvert
    $ export MAKEFLAGS="-j3"
    $ ./minimerge -N --rebuild libidn-1.8 curl-7.16 libjpeg-6b libtiff-3.8 libgd-2.0 geos-3.0 postgis-1.3-py2.5 gdal-1.5 libevent-1.4 memcached-1.2 libmemcache-1.4 cmemcache-0.91 bisonvert-geodjango-r7409 bisonvert

.. note::

    A terme, il suffira de faire un svn switch du minilay de BisonVert, un rm du dossier ``$mt/django/bisonvert``, et un minimerge -N bisonvert.

Système
.......

Les fichiers de conf (apache et postgres) ont changé de place dans la repository, ils sont maintenant checkouté dans le répertoire ``$mt/django/bisonvert/share/conf``. Il faut supprimer le dossier ``/var/makina/bisonvert/conf``:
::

    $ rm -rf /var/makina/bisonvert/conf

Linker les bons fichiers pour apache (en root):
::

    $ rm /etc/apache2/sites-available/50-www.bisonvert.net
    $ rm /etc/apache2/sites-available/51-www2.bisonvert.net
    $ ln -s /var/makina/bisonvert/minitage/django/bisonvert/share/conf/apache/phpnet1/www.bisonvert.net /etc/apache2/sites-available/50-www.bisonvert.net
    $ ln -s /var/makina/bisonvert/minitage/django/bisonvert/share/conf/apache/phpnet1/www2.bisonvert.net /etc/apache2/sites-available/51-www2.bisonvert.net

Hack pour éviter les pb de cache des fichiers compilés avec mod_python:
::

    $ cd $mt/django/bisonvert/shell
    $ ln -s django.python django.www2.python

Editer le fichier ``/etc/profile`` (en root):
::

    PROD_PYTHON="/var/makina/bisonvert/minitage/django/bisonvert/shell/django.python"
    export PROD_PYTHON

(en root):
::

    $ export PROD_PYTHON="/var/makina/bisonvert/minitage/django/bisonvert/shell/django.python"
    $ rm /var/makina/bisonvert/bin/python
    $ ln -s $PROD_PYTHON /var/makina/bisonvert/bin/python

Memcached - 2 solutions:

+ utiliser le memcached compilé par minitage
+ installer memcached sur le système

Procédure de migration
----------------------

Modifications SQL
.................

Charger le script sql ``share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/update_before_data_migration.sql``:
::

    $ cd $mt/django/bisonvert
    $ psql -f share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/update_before_data_migration.sql bisonvert -U bzonvert

Triggers
........

Charger les triggers:
::

    $ psql -f share/data/trigger.sql bisonvert -U bzonvert

Procédures
..........

Charger les procédures:
::

    $ psql -f share/data/procedures.sql bisonvert -U bzonvert

Script shell
............

Lancer le script python ``share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/data_migrator.py`` via le shell:
::

    $ ./shell/django.python ecov/manage.py shell --settings=ecov.conf.settings_www-bisonvert-net < share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/data_migrator.py

Modifications SQL
.................

Charger le script sql ``share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/update_after_data_migration.sql``:
::

    $ psql -f share/data/migrations/from_v1.0.beta_to_v1.0.beta-1.0/update_after_data_migration.sql bisonvert -U bzonvert

Syncdb
......

Faire un syncdb:
::

    $ ./shell/django.python ecov/manage.py syncdb --settings=ecov.conf.settings_www-bisonvert-net

Rétablir l'accès aux site
-------------------------

Enlever la page de maintenance, vérifier que www.bv.net et www2.bv.net sont accessibles.

Apache restart (voir si le reload suffit).
