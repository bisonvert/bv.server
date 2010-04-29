=======================
Créer un nouveau design
=======================

Les étapes à suivre pour créer un nouveau design

Créer un nouveau répertoire
===========================

Créer les dossiers ``media/<new_design>``, ``media/<new_design>/css``, ``media/<new_design>/img``

Dans le dossier ``media/<new_design>/css``, créer des liens symboliques des fichiers ``screen.css``, ``ie-win.css`` et ``ie7-win.css``:
::

    $ cd media/<new_design>/css
    $ ln -s ../../default/css/screen.css
    $ ln -s ../../default/css/ie-win.css
    $ ln -s ../../default/css/ie7-win.css

Copier le fichier theme.css depuis default:
::

    $ cd media/<new_design>/css
    $ cp ../../default/css/theme.css .


**On ne modifie que le fichier theme.css. La structure du site est spécifiée dans le fichier screen.css. Dans la mesure du possible, éviter de changer cette structure.**

Lien symbolique depuis default
==============================

Pour accéder au design via une page spécifique, créer un lien symbolique:
::

    $ cd media/default
    $ ln -s ../<new_design>

Paramétrage
===========

3 nouveaux paramètres ajoutés dans les settings pour l'occasion:

+ ``HOME_PAGES``: dictionnaire qui contient tous les paramètres de chaque design
+ ``HOME_PAGES_AVAILABLE``: liste qui contient les home pages spécifiques accessibles. On construit les urls qui vont bien à l'aide de ce paramètre (cf ``urls.py``)
+ ``THEME_USED``: thème utilisé

Paramètre modifié:
::

    MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, '../media/default/')

``HOME_PAGES`` se définit comme ceci:
::

    HOME_PAGES = {
        'default': {
                'from': None, # departure from bigest cities
                'to': False, # No arrival to
                'dates': (),
                'philosophy': True,
                'title_header': True,
            },
    }

Ajouter le design ``'<new_design>'``.

+ from: villes 'au départ de' affichées dans le footer. Si None, récupère les N plus grandes villes. Si False, pas d'affichage. Sinon, contient une liste d'id des villes que l'ont veut afficher.
+ to: ville 'à destination de' affichées dans le footer. Idem.
+ dates: tuple, contient une liste de dates. Si au moins une date n'est pas dépassée, on affiche un select, sinon un calendrier.
+ philosophy: affiche ou non le bloc philosophy.
+ title_header: affiche ou non le titre BV dans le header.

Les paramètres ``MEDIA_ROOT``, ``HOME_PAGES_AVAILABLE`` et ``THEME_USED`` sont écrasées dans le settings de l'instance utilisée.
