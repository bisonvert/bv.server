def smart_transform(geom, to_srid, clone=True, from_srid=4326):
     """
     Returns a new geometry transformed to the srid given. Assumes if
     the initial geom is lacking an SRS that it is the one given by the
     "from_srid" parameter. (Hence the "smartness" of this function.)
     
     This fixes many silent bugs when transforming between SRSes when the
     geometry is missing this info.

     Original hook from everyblock django application:
     http://code.google.com/p/ebcode
     """
     if not geom.srs:
         geom.srid = from_srid
     t = geom.transform(to_srid, clone=clone)
     return t
