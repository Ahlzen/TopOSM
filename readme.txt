TopOSM - OpenStreetMap Based Topographic Maps

By Lars Ahlzen (lars@ahlzen.com), with contributions from Ian Dees (hosting,
rendering and troubleshooting), Phil Gold (patches and style improvements),
Yves Cainaud (legend), Richard Weait (shield graphics) and others.


Setting up TopOSM rendering - Ubuntu 10.04/10.10/11.04
------------------------------------------------------

Required packages:
python-mapnik mapnik-utils gdal-bin gdal-contrib python-gdal libgdal-dev proj libproj-dev python-pyproj python-numpy imagemagick gcc g++ optipng subversion postgresql postgresql-contrib postgresql-server-dev-8.4 postgis wget libxml2-dev python-libxml2 libgeos-dev libbz2-dev make htop python-cairo python-cairo-dev osm2pgsql unzip python-pypdf libboost-all-dev libicu-dev libpng-dev libjpeg-dev libtiff-dev libz-dev libfreetype6-dev libxml2-dev libproj-dev libcairo-dev libcairomm-1.0-dev python-cairo-dev libpq-dev libgdal-dev libsqlite3-dev libcurl4-gnutls-dev libsigc++-dev libsigc++-2.0-dev

Install additional fonts:
$ sudo apt-get install ttf-sil-gentium ttf-mscorefonts-installer "ttf-adf-*"

Set up PostgreSQL with PostGIS, see:
http://wiki.openstreetmap.org/wiki/Mapnik/PostGIS

Download and build the PerryGeo DEM utilities:
$ sd ~/src
$ svn co http://perrygeo.googlecode.com/svn/trunk/demtools/
$ cd demtools
$ make
$ mkdir -p ~/bin
$ cp bin/* ~/bin
NOTE: To build these, you may need to make the following changes:
* Makefile: GDAL_LIB=-lgdal1.6.0
* Makefile: CPP=g++ -O3 -I/usr/include/gdal
* stringtok.h may require a "using namespace std;" since it's
  included before this directive in some cpp files.

Build local patched Mapnik2:
$ cd ~/src
$ svn co http://svn.mapnik.org/trunk/ mapnik2
$ cd mapnik2
$ patch -p0 < <toposm-dir>/mapnik2_erase_patch.diff
$ python scons/scons.py configure \
    INPUT_PLUGINS=raster,osm,gdal,shape,postgis,ogr \
    PREFIX=$HOME PYTHON_PREFIX=$HOME
$ python scons/scons.py
$ python scons/scons.py install
NOTE: On ubuntu 10.04 you'll need to build a more recent
version of boost. Install locally and add the following flags
to the scons configure step:
    BOOST_INCLUDES=$HOME/include \
    BOOST_LIBS=$HOME/lib

Download required data files:
* http://tile.openstreetmap.org/world_boundaries-spherical.tgz
* http://tile.openstreetmap.org/processed_p.tar.bz2
* http://tile.openstreetmap.org/shoreline_300.tar.bz2
* http://www.naturalearthdata.com/download/10m/cultural/10m-populated-places.zip
* http://www.naturalearthdata.com/download/110m/cultural/110m-admin-0-boundary-lines.zip
* USGS NHD shapefiles: http://www.openstreetmap.us/nhd/
* USGS NED data, as needed: http://openstreetmap.us/ned/13arcsec/grid/
* NLCD 2006 (Land cover) data: http://www.mrlc.gov/nlcd06_data.php
* Planet.osm or other OSM dataset: http://planet.openstreetmap.org/

Modify set-toposm-env, specifying file paths, settings and the
area of interest. Data imports will be limited to the specified
area. Source set-toposm-env:
$ cd <toposm-dir>
$ mkdir -p temp tile
$ . set-toposm-env

Import OSM data, e.g:
$ ./import_planet geodata/osm/Planet.osm

Import NHD data:
$ ./import_nhd

Generate hillshade and colormaps:
$ ./prep_toposm_data

Add a shortcut for your area(s) of interest to areas.py.

Generate the mapnik style files from templates:
$ ./generate_xml

Create contour tables and generate contour lines, for example:
$ ./prep_contours_table
$ ./toposm.py prep WhiteMountains

To render tiles for the specified area and zoom levels:
$ ./toposm.py render WhiteMountains 5 15

To render a PDF, use renderToPdf() in toposm.py
