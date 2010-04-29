======================================
Préparer l'environnement avec Minitage
======================================

.. highlight:: sh

Pour avoir une idée du fonctionnement de minitage, lire la `doc en ligne`_.

Installer BisonVert avec minitage
=================================

Dans cette page, on construit un environnement de dev pour le trunk de BisonVert (minilay bisonvert-dev).

Installation minitage 0.4

Dépendances système
-------------------

::

    apt-get install build-essential subversion m4 libtool pkg-config autoconf gettext bzip2

Variables d'environnement
-------------------------

+ ``$mt``: path vers le répertoire minitage (par exemple ``~/minitage``)
+ ``$mypy``: endroit du python de bootstrap (par exemple ``~/tools/python``)

Pour positionner ces variables:
::

    export mt=~/minitage
    export mypy=~/tools/python

On peut mettre ces 2 lignes dans son bashrc ou son zshrc.

Configurer buildout
-------------------

Configurer buildout pour toujours télécharger au même endroit:
::

    mkdir -p ~/.buildout/downloads
    cat << EOF > ~/.buildout/default.cfg
    [buildout]
    download-directory = $HOME/.buildout/downloads
    download-cache = $HOME/.buildout/downloads
    EOF

Installer le bootstrappeur
--------------------------

Installer le bootstrappeur, un python qui va bien, à utiliser avec virtualenv:
::

    mkdir -p $mypy
    cd $mypy
    wget http://hg.minitage.org/hg/minitage/shell/raw-file/tip/PyBootstrapper.sh
    bash ./PyBootstrapper.sh $mypy

Mettre virtualenv
-----------------

::

    mkdir $mt
    $mypy/bin/virtualenv --no-site-packages $mt

Activer le virtualenv:
::

    source $mt/bin/activate

**Activation à faire avant chaque manip minitage.**

Installer minitage
------------------

Installation:
::

    cd $mt
    source $mt/bin/activate
    easy_install -U minitage.core minitage.paste

Synchronisation des packages minitage:
::

    minimerge -s


Installer le minilay du projet
------------------------------

::

    cd $mt/minilays
    svn co https://subversion.makina-corpus.net/bisonvert/trunk/minitage/minilays/bisonvert

Minimerge de BisonVert
----------------------

LE truc qui prend du temps:
::

    cd $mt
    minimerge bisonvert-dev

Postgres
========

Création d'un profil pg:
::

    cd $mt
    $mt/bin/paster create -t minitage.profils.postgresql bisonvert-dev
    Selected and implied templates:
      minitage.paste#minitage.profils.env         Template for creating a file to source to get the needed environnment variables relative to a minitage project.
      minitage.paste#minitage.profils.postgresql  Template for creating an instance of postresql in the sys dir of a minitage project.

    Variables:
      egg:      bisonvert_dev
      package:  bisonvertdev
      project:  bisonvert-dev


        Warning: All minitage templates come by default with their dependencies. You ll not have to specify them.


    Enter project_dependencies (Dependencies (separated by comma)) ['']: 
    Enter project_eggs (Python packages non-eggified like libxml2 to be added to the python path (separated by comma)) ['']: 
    Enter db_name (Database name) ['minitagedb']: bv
    Enter db_user (Default user) ['zebuline']: 
    Enter db_group (Default group) ['zebuline']: 
    Enter db_host (Host to listen on) ['localhost']: 
    Enter db_port (Port to listen to) ['5432']: 5434

Laisser le default user et le default group. La bdd est créée automatiquement, et appartient à db_user. Penser à modifier le port si un pg est déjà installé sur le système. (Penser par la suite à renseigner ce numéro de port dans le fichier de settings, voir :ref:`install-install_bv-settings-label`)

Démarrer pg:
::

    cd $mt/django/bisonvert-dev
    source sys/share/minitage/minitage.env
    ./sys/etc/init.d/bv.postgresql start

Le nom du script d'init dépend du nom de la bdd renseigné lors de la création du profil, ici bv.

Tester geos et gdal
===================

::

    djangopy

Tester gdal
-----------

Dans la console python:
::

    >>> from django.contrib.gis.gdal import HAS_GDAL
    >>> print HAS_GDAL
    True
    >>> from django.contrib.gis.tests import test_gdal
    >>> test_gdal.run()
    .....
    BEGIN - expecting out of range feature id error; safe to ignore.

    ERROR 1: Attempt to read shape with feature id (50000) out of available range.
    ERROR 1: Attempt to read shape with feature id (50000) out of available range.

    END - expecting out of range feature id error; safe to ignore.
    ....................
    BEGIN - expecting IllegalArgumentException; safe to ignore.

    ERROR 1: IllegalArgumentException: points must form a closed linestring

    END - expecting IllegalArgumentException; safe to ignore.

    ......................
    ----------------------------------------------------------------------
    Ran 47 tests in 0.154s

    OK

Tester geos
-----------

Dans la console python:
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
    Testing equivalence. ... ok
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
    Testing pickling and unpickling support. ... ok

    ----------------------------------------------------------------------
    Ran 36 tests in 0.347s

    OK

Remarque
========

Si vous avez des trucs du genre apres le source du .env:
::

    (minitage-bisonvert) kiorky@judith:~/minitage/mt/django/bisonvert$ vim
    vim: symbol lookup error: /home/kiorky/minitage/mt/dependencies/python-2.5/parts/part/lib/libpython2.5.so.1.0: undefined symbol: emacs_meta_keymap

Solution:
::

    unset LD_LIBRARY_PATH

Déployer BisonVert
==================

Avant de faire quoique ce soit avec le projet, charger le .env de bisonvert:
::

    source $mt/django/bisonvert-dev/sys/share/minitage/minitage.env

cf :ref:`install-install_bv-label`

Lancer Bisonvert !
==================

::

    cd $mt/django/bisonvert-dev/src/bisonvert/src
    bv_manage runserver --settings=<SETTINGS_FILE> 0.0.0.0:8000

Voila, normalement ça marche ...

.. _`doc en ligne`: http://minitage.org/doc/index.html
