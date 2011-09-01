TopOSM - OpenStreetMap Based Topographic Maps

By Lars Ahlzen (lars@ahlzen.com), with contributions from:
Ian Dees (hosting, rendering and troubleshooting)
Phil Gold (patches and style improvements)
Yves Cainaud (legend)
Richard Weait (shield graphics)
and others.


Requirements:
-------------
* Standard UN*X tools (bash, sed, awk, ...)
* Mapnik
* PostgreSQL
* _int.sql (from postgresql-contrib) for PostgreSQL
* PostGIS
* 900913.sql projection (from osm2pgsql) for PostGIS
* Python 2.5/2.6, with:
  - Numpy
  - Mapnik
* Imagemagick
* GDAL/OGR (including utility programs)
* osm2pgsql (for planet import)
* shp2pgsql (for NHD import)
* Perrygeo DEM tools (hillshade, color-relief)
  See: http://www.perrygeo.net/wordpress/?p=7
* OptiPNG (for tile optimization)

Data needed:
------------
* builtup_area.shp (from OSM svn, mapnik)
* processed_p.shp (from OSM svn, mapnik)
* world_bnd_m.shp (from OSM svn, mapnik)
* USGS NED 1/3" http://openstreetmap.us/ned/13arcsec/grid/
  (you can use the supplied get_ned script)
* USGS NHD http://www.openstreetmap.us/nhd/
* Planet.osm http://planet.openstreetmap.org/
  (or other OSM data dump)

Setup
-----
* Build/install requirements (see above).
* Download required data sets.
* Setup PostgreSQL with PostGIS. See OSM wiki.
* Create a PostGIS database.
* Modify and source set-toposm-env.
* Run import_planet.
* Run import_nhd.
* Run prep_contours_table.

Render an area:
---------------
This example will render the area UTM19T (defined in areas.py) from
zoom level 5 through 15:

$ source set-toposm-env
$ python
>>> import toposm
>>> import areas
>>> toposm.prepareData(areas.UTM19T)
>>> toposm.renderTiles(areas.UTM19T, 5, 15)
$ optimize_png.py tile/contours
$ optimize_png.py tile/features


Notes:
------
Make sure that you have plenty of disk space for temporary
files and tiles, and database space for contour lines.

Preprocessed data files (such as the hillshade and colormap
images) are stored in the temp directory. Empty .shp files are also
left here to mark areas where contours have already been imported
into the database. NOTE: If you clear the data in this directory,
you should also delete all data from the contours table, or you
risk ending up with duplicated contours the next time you run
prepareData.

In TopOSM, rendering quality takes precedence over speed. You'll
notice.
