========
A propos
========

Nous parlons du projet BisonVert. Pour des raisons historiques, le projet au sens django du terme se nomme ecov.

Documentation
=============

Documentation écrite en `REStructured Text`_, grâce au projet `Sphinx`_.

Elle est compatible Sphinx0.2 et Sphinx0.3, mais ne l'est plus pour Sphinx0.1.

Installer Sphinx:
::

    $ easy_install Sphinx

Compiler la doc:
::

    $ cd /path/to/project/app/share/docs
    $ make clean html

Qualité
=======

Gestion de conf
---------------

+ Interdiction formelle de commiter sur un tag: un tag peut être créé mais surtout pas modifié.
+ En prod, on déploie des tags et non des branches.

Langue
------

Le code est en anglais. Les commentaires sont en anglais. Les docstrings, utilisées dans cette doc, sont en français.

La documentation est écrite en français.

Revue de code
-------------

Les mails de commit sont disponibles dans les folders imap partagés: ``shared/archives/bisonvert-commit``

Pytlint - TODO
--------------

TODO

Liens utiles
============

+ `GeoDjango`_
+ TODO: lien vers la page django de la doc makina

IRC
===

+ #ecov sur OFTC (irc.oftc.net - chan du projet)
+ #django-fr sur Freenode (irc.freenode.net)
+ #geodjango sur Freenode (en anglais, gros avantage: jbronn est sur ce chan)
+ #minitage sur Freenode pour taper kiorky si minitage marche pas :)


.. _`REStructured Text`: http://en.wikipedia.org/wiki/ReStructuredText
.. _`Sphinx`: http://sphinx.pocoo.org/
.. _`GeoDjango`: http://code.djangoproject.com/wiki/GeoDjango
