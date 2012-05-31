#!/usr/bin/python

"""env.py: Initializes the TopOSM render environment."""

import os
import sys

__author__      = "Lars Ahlzen"
__copyright__   = "(c) Lars Ahlzen 2008-2011"
__license__     = "GPLv2"


##### Import environment variables

# Check that the environment is set and import configuration
if not 'TOPOSM_ENV_SET' in os.environ:
    print "Error: TopOSM environment not set."
    sys.exit(1)

BASE_TILE_DIR = os.environ['BASE_TILE_DIR']
CONTOURS_TABLE = os.environ['CONTOURS_TABLE']
DATABASE = os.environ['DB_NAME']
TEMPDIR = os.environ['TEMP_DIR']
NED13DIR = os.environ['NED13_DIR']
COLORFILE = os.environ['COLORFILE']
NUM_THREADS = int(os.environ['RENDER_THREADS'])
TILE_SIZE = int(os.environ['TILE_SIZE'])
BORDER_WIDTH = int(os.environ['BORDER_WIDTH'])
ERRORLOG = os.environ['ERROR_LOG']
JPEG_QUALITY = os.environ['JPEG_QUALITY']
TOPOSM_DEBUG = os.environ['TOPOSM_DEBUG']
EXTRA_FONTS_DIR = os.environ['EXTRA_FONTS_DIR']

##### Common constants

#CONTOUR_INTERVAL = 15.24 # 50 ft in meters
#CONTOUR_INTERVAL = 7.62 # 25 ft in meters
CONTOUR_INTERVAL = 12.192 # 40 ft in meters

MAPNIK_LAYERS = ['hypsorelief', 'landcoverrelief', 'areas', 'ocean', 'contours', 'features']

# Optimal metatile size (N x N subtiles) by zoom level.
# A too low number is inefficient. A too high number uses
# large amounts of memory and sometimes breaks the gdal tools.
NTILES = {
    1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1,
    11:2, 12:4, 13:6, 14:8, 15:10, 16:12, 17:12, 18:12,
    19:12, 20:12 }

LATLONG_PROJECTION_DEF = "+proj=latlong"
MERCATOR_PROJECTION_DEF = "+proj=merc +a=6378137 +b=6378137 " + \
    "+lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m " + \
    "+nadgrids=@null +no_defs +over"
NAD83_PROJECTION_DEF = "+proj=latlong +datum=NAD83 +ellps=GRS80 +no_defs"

