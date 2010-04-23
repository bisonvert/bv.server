.. _howto-start_django_server-label:

=================================
Démarrer le serveur django de dev
=================================

Cas pratique: On utilise le fichier de configuration ecov.conf.settings_local.

Pour lancer le serveur django de dev, on fait:
::

    $ cd /path/to/project/
    $ python ecov/manage.py runserver --settings=ecov.conf.settings_local 0.0.0.0:8000

.. note::

    Pour une raison encore inconnue, il arrive que le PYTHONPATH soit mal
    positionné quand on utilise le script manage.py depuis le répertoire
    /path/to/project/ecov/. Il vaut mieux travailler depuis le répertoire
    parent et lancer ecov/manage.py
