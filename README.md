# TopOSM #

A system for rendering OpenStreetMap Based Topographic Maps


## Requirements ##

TopOSM runs on Linux. It may be possible to build and run it on other platforms, but I have not tested this. If you try it, please let me know.

TopOSM depends on some fairly recent software, including:

* Mapnik (2.0) with included patches and Cairo support
* Python (2.6)
* GDAL (1.7)
* PostgreSQL + PostGIS
* ImageMagick

(later versions than those mentioned above will probably work)


## Installation ##

Required packages will vary depending on your distribution. For Ubuntu 11.04, this list of packages may be a good start:

    python-mapnik mapnik-utils gdal-bin gdal-contrib python-gdal
    libgdal-dev proj libproj-dev python-pyproj python-numpy imagemagick
    gcc g++ optipng subversion postgresql postgresql-contrib
    postgresql-server-dev-8.4 postgis wget libxml2-dev python-libxml2
    libgeos-dev libbz2-dev make htop python-cairo python-cairo-dev
    osm2pgsql unzip python-pypdf libboost-all-dev libicu-dev libpng-dev
    libjpeg-dev libtiff-dev libz-dev libfreetype6-dev libxml2-dev
    libproj-dev libcairo-dev libcairomm-1.0-dev python-cairo-dev
    libpq-dev libgdal-dev libsqlite3-dev libcurl4-gnutls-dev
    libsigc++-dev libsigc++-2.0-dev ttf-sil-gentium
    ttf-mscorefonts-installer "ttf-adf-*"

Set up PostgreSQL with PostGIS, see:
http://wiki.openstreetmap.org/wiki/Mapnik/PostGIS


### Build local patched Mapnik ###

```
$ git clone https://github.com/mapnik/mapnik.git
$ cd mapnik
$ patch -p0 < <toposm-dir>/mapnik2_erase_patch.diff
$ python scons/scons.py configure \
    INPUT_PLUGINS=raster,osm,gdal,shape,postgis,ogr \
    PREFIX=$HOME PYTHON_PREFIX=$HOME
$ python scons/scons.py
$ python scons/scons.py install
```

If you need a more recent boost than available for your system, you can build one locally (i.e. with PREFIX=$HOME) and tell the mapnik configure step to link against that by adding:

```
BOOST_INCLUDES=$HOME/include BOOST_LIBS=$HOME/lib
```


### Required data files ###

* http://tile.openstreetmap.org/world_boundaries-spherical.tgz
* http://tile.openstreetmap.org/processed_p.tar.bz2
* http://tile.openstreetmap.org/shoreline_300.tar.bz2
* http://www.naturalearthdata.com/download/10m/cultural/10m-populated-places.zip
* http://www.naturalearthdata.com/download/110m/cultural/110m-admin-0-boundary-lines.zip
* USGS NHD shapefiles: http://www.openstreetmap.us/nhd/
* USGS NED data, as needed: http://openstreetmap.us/ned/13arcsec/grid/
* NLCD 2006 (Land cover) data: http://www.mrlc.gov/nlcd06_data.php
* Planet.osm or other OSM dataset: http://planet.openstreetmap.org/
* Water polygons (in spherical mercator) from http://openstreetmapdata.com/


### Configuring the Rendering Environment ###

Create the required directories for tiles and temp files:

```
$ mkdir -p temp tile
```

TopOSM is configured through environment variables. A template for this is included. Make a copy, modify it according to you system, and source it:

```
$ cp set-toposm-env.templ set-toposm-env
$ emacs set-toposm-env
$ . set-toposm-env
```

Import OSM data. The import will be cropped to the area specified in set-toposm-env.
```
$ ./import_planet geodata/osm/Planet.osm
```

The import script can also import OSM daily diffs (ending in .osc.gz).


Import NHD data:
```
$ ./import_nhd
```

Generate hillshade and colormaps:
```
$ ./prep_toposm_data
```

Add a shortcut for your area(s) of interest to areas.py.

Generate the mapnik style files from templates:
```
$ ./generate_xml
```
(you need to do this every time you modify the styles in the
templates and include directories)

Create contour tables and generate contour lines, for example:
```
$ ./prep_contours_table
$ ./toposm.py prep WhiteMountains
```

To render tiles for the specified area and zoom levels:
```
$ ./toposm.py render WhiteMountains 5 15
```

To render a PDF, use renderToPdf() in toposm.py


## Credits ##

Created by Lars Ahlzen (lars@ahlzen.com), with contributions from Ian Dees (hosting, rendering and troubleshooting), Phil Gold (patches and style improvements), Kevin Kenny (improved NHD rendering, misc patches), Yves Cainaud (legend), Richard Weait (shield graphics) and others.

License: GPLv2
