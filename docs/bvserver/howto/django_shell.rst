.. _howto-django_shell-label:

======================
Lancer un shell Django
======================

Pour lancer un shell django sur nos différentes plateformes.

Production
==========

::

    $ export mt=/var/makina/bisonvert/minitage
    $ cd $mt/django/bisonvert
    $ ./shell/django.python ecov/manage.py shell --settings=<SETTINGS_FILE>

Xenecov
=======

::

    $ cd /var/www/ecov_svn
    $ sudo python ecov/manage.py shell --settings=ecov.conf.settings_xenecov

.. note::

    GDAL_DATA est positionné dans le fichier de settings.