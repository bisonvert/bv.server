BisonVert client
================

This repository is the main repository of a client wrote in django, for
bisonvert, a carpooling system.

What is Bisonvert ?
-------------------

Bisonvert is a simple carpooling web application. The primary goal is to match
carpool demands with carpool offers.

The infrastructure is in 4 parts, which can all be found in the bitbucket page
http://bitbucket.org/bisonvert/.

The server
~~~~~~~~~~

The main application logic of the carpooling service is contained in the server.
This includes:

* A carpooling system: basic operations on offer/demand.
* A ranking system for the users.
* A system to contact the users.
* Availability of the data trought an API
* A management system for API tokens (oauth)

The server uses internally Python and Django for the web application, PostGIS
for Geographic informations and requests, and Mapnik to return the layers.

The server *does not* provides a web interface to create and search trips: this
is the role of the client.

Installation
------------

You can both install bisonvert from the mercurial repositories, using pip or minitage (recommended).

Pip install
~~~~~~~~~~~

The best way is to install bisonvert from pip::

    $ pip install bv.server

Minitage installation (recommended way)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you dont have minitage::
    
    easy_install -U virtualenv
    virtualenv --no-site-packages --distribute ~/minitage
    source ~/minitage/bin/activate
    easy_install -U minitage.core minitage.paste

In a minitage ::    

    cd  ~/minitage/minilays
    hg clone https://bitbucket.org/kiorky/bisonvert-minilay
    # install the project
    minimerge bv.server
    # intiate a postgresql db with postgis inside
    paster create -t minitage.instances.postgresql bv.server db_name=bv db_user=bv db_port=5434 db_password=secret --no-interactive
    bv.createlang plpgsql
    bv.createlang c
    bv.psql  -U $(whoami)  -f ../../dependencies/postgresql-8.4/parts/part/share/contrib/postgis.sql 
    bv.psql  -U $(whoami)  -f ../../dependencies/postgresql-8.4/parts/part/share/contrib/spatial_ref_sys.sql 
 
    

Launch bisonvert-server
~~~~~~~~~~~~~~~~~~~~~~~~

To launch the client, just go to the source lib, and do::

    $ python manage.py runserver

