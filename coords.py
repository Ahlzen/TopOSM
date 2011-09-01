#!/usr/bin/python

"""coords.py: Coordinate transformation functions for TopOSM"""

from math import pi, cos, sin, log, exp, atan, ceil, floor
from env import *;

# Use mapnik2 if available, mapnik otherwise.
try:
    import mapnik2 as mapnik
    from mapnik2 import Coord, Box2d, Projection
except ImportError:
    import mapnik
    from mapnik import Coord
    from mapnik import Projection
    from mapnik import Envelope as Box2d

__author__      = "Lars Ahlzen"
__copyright__   = "(c) Lars Ahlzen 2008-2011"
__license__     = "GPLv2"


# NOTE: In pixel and tile coordinates, the Y-coordinate
# increases towards the south, which is opposite the standard
# notation for latitudes.

# NOTE: Lon/Lat coordinates are assumed to be given in WGS84 unless
# otherwise specified.


DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

def minmax (a,b,c):
    a = max(a,b)
    a = min(a,c)
    return a

# Based on code from generate_tiles.py
class GoogleProjection:    
    def __init__(self, levels=22):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0, levels):
            e = c / 2;
            self.Bc.append(c / 360.0)
            self.Cc.append(c / (2 * pi))
            self.zc.append((e, e))
            self.Ac.append(c)
            c *= 2
                
    def LLToPixel(self, coord, zoom):
         d = self.zc[zoom]
         e = round(d[0] + coord.x * self.Bc[zoom])
         f = minmax(sin(DEG_TO_RAD * coord.y), -0.9999, 0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f)) * -self.Cc[zoom])
         return Coord(e, g)
     
    def pixelToLL(self, coord, zoom):
         e = self.zc[zoom]
         f = (coord.x - e[0]) / self.Bc[zoom]
         g = (coord.y - e[1]) / -self.Cc[zoom]
         h = RAD_TO_DEG * (2 * atan(exp(g)) - 0.5 * pi)
         return Coord(f, h)
    
    def envLLToPixel(self, env, zoom):
        lb = self.LLToPixel(Coord(env.minx, env.miny), zoom)
        rt = self.LLToPixel(Coord(env.maxx, env.maxy), zoom)
        return Box2d(lb.x, lb.y, rt.x, rt.y)

    def envPixelToLL(self, env, zoom):
        lb = self.pixelToLL(Coord(env.minx, env.miny), zoom)
        rt = self.pixelToLL(Coord(env.maxx, env.maxy), zoom)
        return Box2d(lb.x, lb.y, rt.x, rt.y)


GOOGLE_PROJECTION = GoogleProjection()
LATLONG_PROJECTION = Projection(LATLONG_PROJECTION_DEF)
MERCATOR_PROJECTION = Projection(MERCATOR_PROJECTION_DEF)


##### Geographic coordinate transformation

def LLToMerc(coord):
    """Converts a Coord(lon,lat) or Box2d(l,b,r,t) to
    OSM Mercator (x,y)."""
    return MERCATOR_PROJECTION.forward(coord)

def mercToLL(coord):
    """Converts an OSM Mercator Coord(x,y) or Box2d(l,b,r,t)
    to (lon,lat)."""
    return MERCATOR_PROJECTION.inverse(coord)

def LLToPixel(coord, z):
    """Converts a Coord(lon,lat) or Box2d(l,b,r,t) to
    OSM (x,y) pixel coordinates at the specified zoom level."""
    if isinstance(coord, Coord):
        return GOOGLE_PROJECTION.LLToPixel(coord, z)
    else:
        return GOOGLE_PROJECTION.envLLToPixel(coord, z)

def pixelToLL(coord, z):
    """Converts an OSM pixel Coord(x,y) or Box2d(l,b,r,t)
    to (lon,lat) at the specified zoom level."""
    if isinstance(coord, Coord):
        return GOOGLE_PROJECTION.pixelToLL(coord, z)
    else:
        return GOOGLE_PROJECTION.envPixelToLL(coord, z)

def pixelToMerc(coord, z):
    """Converts an OSM pixel Coord(x,y) or Box2d(l,b,r,t)
    to OSM Mercator (x,y) at the specified zoom level."""
    # No direct transformation. Use px->ll->merc.
    if isinstance(coord, Coord):
        ll = GOOGLE_PROJECTION.pixelToLL(coord, z)
    else:
        ll = GOOGLE_PROJECTION.envPixelToLL(coord, z)
    return MERCATOR_PROJECTION.forward(ll)

def mercToPixel(coord, z):
    """Converts an OSM Mercator Coord(x,y) or Box2d(l,b,r,t)
    to OSM pixel coordinates (x,y) at the specified zoom level."""
    # No direct transformation. Use merc->ll->pixel.
    ll = MERCATOR_PROJECTION.inverse(coord)
    if isinstance(coord, Coord):
        return GOOGLE_PROJECTION.LLToPixel(ll, z)
    else:
        return GOOGLE_PROJECTION.envLLToPixel(ll, z)


##### Tile coordinates

def getPixelTileEnv(x, y, ntiles = 1, includeBorder = True):
    """Returns the OSM Pixel coordinate Box2d for the tile(s) for
    the specified tile(s)."""
    border = 0
    size = TILE_SIZE * ntiles
    if includeBorder:
        border = BORDER_WIDTH
    return Box2d(
        x * size - border,
        y * size - border,
        (x+1) * size + border,
        (y+1) * size + border)

def getLLTileEnv(z, x, y, ntiles = 1, includeBorder = True):
    """Returns the lon/lat Box2d for the tile(s) at the specified
    tile coordinates."""
    return pixelToLL(getPixelTileEnv(x, y, ntiles, includeBorder), z)

def getMercTileEnv(z, x, y, ntiles = 1, includeBorder = True):
    """Returns the OSM Mercator Box2d for the tile(s) at the specified
    tile coordinates."""
    return pixelToMerc(getPixelTileEnv(x, y, ntiles, includeBorder), z)

def getTileAtLL(coord, z, ntiles = 1):
    """Returns the OSM tile coordinates (x, y) at the specified
    Coord(lon,lat) and zoom level."""
    px = LLToPixel(coord, z)
    size = TILE_SIZE * ntiles
    return ((int)(px.x / size), (int)(px.y / size))

def getTileRange(envLL, z, ntiles = 1):
    """Returns the tile number range (fromx, tox, fromy, toy)
    that covers the Box2d at the specified zoom level."""
    topleft = Coord(envLL.minx, envLL.maxy)
    bottomright = Coord(envLL.maxx, envLL.miny)
    tltile = getTileAtLL(topleft, z, ntiles)
    brtile = getTileAtLL(bottomright, z, ntiles)
    return (tltile[0], brtile[0], tltile[1], brtile[1])

