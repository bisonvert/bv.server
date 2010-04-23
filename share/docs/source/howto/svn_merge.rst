==================
Faire un svn merge
==================

Petite note interne, comment merger les modifs effectuées sur une branche dans une autre branche.

+ ``n``: révision depuis laquelle on veut merger
+ ``m``: dernière révision qu'on veut merger, incluse
+ ``branche_from``: branche source (qu'on veut merger)
+ ``branche_to``: branche destination (dans laquelle on veut merger)

On veut merger les révisions n à m effectuées sur la branche_from dans la
branche_to:
::

    $ cd <path_to_project>/branche_to
    $ svn merge -r(n-1):m <URL_branche_from> .

Option --dry-run pour vérifier.

Exemple: On doit merger les révisions 454 à 488 effectuées sur la branche bisonvert.v1.0.beta dans le trunk:
::

    $ cd <path_to_project>/trunk
    $ svn merge -r453:488 https://subversion.makina-corpus.net/bisonvert/branches/bisonvert.v1.0.beta .

Exemple de message de commit:
::

    Merge des revisions 454:488 via svnmerge from branches/bisonvert.v1.0.beta to trunk
