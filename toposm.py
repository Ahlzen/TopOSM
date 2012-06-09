#!/usr/bin/python

"""toposm.py: Functions to control TopOSM rendering."""

import sys, os, time, threading
import numpy
import multiprocessing
import cairo

from Queue import Queue
from os import path
from subprocess import call

# PyPdf is optional, but render-to-pdf won't work without it.
try:
    from pyPdf import PdfFileWriter, PdfFileReader
except ImportError:
    print "WARNING: PyPdf not found. Render to PDF will not work."

# Use mapnik2 if available
try:
    import mapnik2 as mapnik
    from mapnik2 import Coord, Box2d
except ImportError:
    import mapnik
    from mapnik import Coord
    from mapnik import Envelope as Box2d

from env import *
from coords import *
from common import *
import NED
import areas
from JobManager import JobManager

__author__      = "Lars Ahlzen and contributors"
__copyright__   = "(c) Lars Ahlzen and contributors 2008-2011"
__license__     = "GPLv2"


##### Initialize Mapnik

# Import extra fonts
if EXTRA_FONTS_DIR != '':
    mapnik.register_fonts(EXTRA_FONTS_DIR)

# Check for cairo support
if not mapnik.has_cairo():
    print "ERROR: Your mapnik does not have Cairo support."
    sys.exit(1)


##### Render settings

# Set to true to save intermediate layers that are normally
# merged. Primarily useful for debugging and style editing.
SAVE_INTERMEDIATE_TILES = True

# Enables/disables saving the composite layers
SAVE_PNG_COMPOSITE = True
SAVE_JPEG_COMPOSITE = True
JPEG_COMPOSITE_QUALITY = 90

# Enable/disable the use of the cairo renderer altogether
USE_CAIRO = True


class RenderThread:
    def __init__(self, q, maxz, threadNumber):
        self.q = q
        self.maxz = maxz
        self.threadNumber = threadNumber
        self.currentz = 0
        
    def init_zoomlevel(self, z):
        self.currentz = z
        self.tilesize = getTileSize(NTILES[z], True)
        self.maps = {}
        for mapName in MAPNIK_LAYERS:
            console.debugMessage('Loading mapnik.Map: ' + mapName)
            self.maps[mapName] = mapnik.Map(self.tilesize, self.tilesize)
            mapnik.load_map(self.maps[mapName], mapName + ".xml")

    def runAndLog(self, message, function, args):
        message = '[%02d] %s' % (self.threadNumber+1,  message)
        console.printMessage(message)
        try:
            function(*args)        
        except Exception as ex:
            console.printMessage('Failed: ' + message)
            errorLog.log('Failed: ' + message, ex)
            raise

    def renderMetaTile(self, z, x, y):
        ntiles = NTILES[z]
        if (z != self.currentz):
            self.init_zoomlevel(z)
        if not (allConstituentTilesExist(z, x, y, ntiles)):
            msg = "Rendering meta tile %s %s %s (%sx%s)" % \
                (z, x, y, ntiles, ntiles)
            self.runAndLog(msg, renderMetaTile, (z, x, y, ntiles, self.maps))

    def renderLoop(self):
        self.currentz = 0
        while True:
            r = self.q.get()
            if (r == None):
                self.q.task_done()
                break
            self.renderMetaTile(*r)
            self.q.task_done()


def getMetaTileDir(mapname, z):
    return path.join(BASE_TILE_DIR, mapname, str(z))

def getMetaTilePath(mapname, z, x, y, suffix = "png"):
    return path.join(getMetaTileDir(mapname, z), \
        's' + str(x) + '_' + str(y) + '.' + suffix)

def metaTileExists(mapname, z, x, y, suffix = "png"):
    return path.isfile(getMetaTilePath(mapname, z, x, y, suffix))

def getTileDir(mapname, z, x):
    return path.join(getMetaTileDir(mapname, z), str(x))

def getTilePath(mapname, z, x, y, suffix = "png"):
    return path.join(getTileDir(mapname, z, x), str(y) + '.' + suffix)

def tileExists(mapname, z, x, y, suffix = "png"):
    return path.isfile(getTilePath(mapname, z, x, y, suffix))

def getTileSize(ntiles, includeBorder = True):
    if includeBorder:
        return TILE_SIZE * ntiles + 2 * BORDER_WIDTH
    else:
        return TILE_SIZE * ntiles
        
def allTilesExist(mapname, z, fromx, tox, fromy, toy, suffix = "png"):
    for x in range(fromx, tox+1):
        for y in range(fromy, toy+1):
            if not tileExists(mapname, z, x, y, suffix):
                return False
    return True
            
def allConstituentTilesExist(z, x, y, ntiles):
    fromx = x*ntiles
    tox = (x+1)*ntiles - 1
    fromy = y*ntiles
    toy = (y+1)*ntiles - 1
    # NOTE: This only checks for the final "composite" tile set(s)...
    if SAVE_PNG_COMPOSITE:
        chExists = allTilesExist('composite_h', z, fromx, tox, fromy, toy, 'png')
        clExists = allTilesExist('composite_l', z, fromx, tox, fromy, toy, 'png')
        if (not chExists) or (not clExists):
            return False
    if SAVE_JPEG_COMPOSITE:
        jhExists = allTilesExist('jpeg90_h', z, fromx, tox, fromy, toy, 'jpg')
        jlExists = allTilesExist('jpeg90_l', z, fromx, tox, fromy, toy, 'jpg')
        if (not jhExists) or (not jlExists):
            return False
    return True

def renderMetaTile(z, x, y, ntiles, maps):
    """Renders the specified map tile and saves the result (including the
    composite) as individual tiles."""
    hypsorelief = renderLayer('hypsorelief', z, x, y, ntiles, maps['hypsorelief'], 'png')
    landcoverrelief = renderLayer('landcoverrelief', z, x, y, ntiles, maps['landcoverrelief'], 'png')
    areas = renderLayer('areas', z, x, y, ntiles, maps['areas'], 'png')
    ocean = renderLayer('ocean', z, x, y, ntiles, maps['ocean'], 'png', True)
    contours = renderLayer('contours', z, x, y, ntiles, maps['contours'], 'png', True)
    features = renderLayer('features', z, x, y, ntiles, maps['features'], 'png', True)
    base_h = getComposite((hypsorelief, areas, ocean))
    base_l = getComposite((landcoverrelief, ocean))
    composite_h = getComposite((base_h, contours, features))
    composite_l = getComposite((base_l, contours, features))
    if SAVE_PNG_COMPOSITE:
        saveTiles(z, x, y, ntiles, 'composite_h', composite_h)
        saveTiles(z, x, y, ntiles, 'composite_l', composite_l)
    if SAVE_JPEG_COMPOSITE:
        basename = 'jpeg' + str(JPEG_COMPOSITE_QUALITY)
        saveTiles(z, x, y, ntiles, basename+'_h', composite_h, 'jpg', basename)
        saveTiles(z, x, y, ntiles, basename+'_l', composite_l, 'jpg', basename)
    if SAVE_INTERMEDIATE_TILES:
        saveTiles(z, x, y, ntiles, 'base_h', base_h)
        saveTiles(z, x, y, ntiles, 'base_l', base_l)
        saveTiles(z, x, y, ntiles, 'contours', contours)
        saveTiles(z, x, y, ntiles, 'hypsorelief', hypsorelief)
        saveTiles(z, x, y, ntiles, 'landcoverrelief', landcoverrelief)
        saveTiles(z, x, y, ntiles, 'areas', areas)
        saveTiles(z, x, y, ntiles, 'ocean', ocean)
        saveTiles(z, x, y, ntiles, 'features', features)
    
def renderLayer(name, z, x, y, ntiles, map, suffix = 'png', useCairo = False):
    """Renders the specified map tile (layer) as a mapnik.Image."""
    console.debugMessage(' Rendering layer: ' + name)
    env = getMercTileEnv(z, x, y, ntiles, True)
    tilesize = getTileSize(ntiles, True)
    map.zoom_to_box(env)
    if useCairo and USE_CAIRO:
        assert mapnik.has_cairo()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, tilesize, tilesize)
        mapnik.render(map, surface)
        image = mapnik.Image.from_cairo(surface)
    else:            
        image = mapnik.Image(tilesize, tilesize)
        mapnik.render(map, image)
    return image

def saveTiles(z, x, y, ntiles, mapname, image, suffix = 'png', imgtype = None):
    """Saves the individual tiles from a metatile image."""
    for dx in range(0, ntiles):
        tilex = x*ntiles + dx
        ensureDirExists(getTileDir(mapname, z, tilex))
        for dy in range(0, ntiles):    
            tiley = y*ntiles + dy
            offsetx = BORDER_WIDTH + dx*TILE_SIZE
            offsety = BORDER_WIDTH + dy*TILE_SIZE
            view = image.view(offsetx, offsety, TILE_SIZE, TILE_SIZE)
            if imgtype:
                view.save(getTilePath(mapname, z, tilex, tiley, suffix), imgtype)
            else:
                view.save(getTilePath(mapname, z, tilex, tiley, suffix))

def getComposite(images):
    """Composites (stacks) the specified images, in the given order."""
    composite = mapnik.Image(images[0].width(), images[0].height())
    for image in images:
        composite.blend(0, 0, image, 1.0)
    return composite


##### Public methods

def toposmInfo():
    print "Using mapnik version:", mapnik.mapnik_version()
    print "Has Cairo:", mapnik.has_cairo()
    print "Fonts:"
    for face in mapnik.FontEngine.face_names():
        print "\t", face

def prepareData(envLLs):
    if not hasattr(envLLs, '__iter__'):
        envLLs = (envLLs,)
    manager = JobManager()
    for envLL in envLLs:
        tiles = NED.getTiles(envLL)        
        for tile in tiles:
            manager.addJob("Preparing %s" % (tile[0]), NED.prepDataFile, tile)
    manager.finish()
    
    console.printMessage("Postprocessing contours...")
    NED.removeSeaLevelContours()
    NED.simplifyContours(1.0)
    NED.convertContourElevationsToFt()
    NED.clusterContoursOnGeoColumn()
    NED.analyzeContoursTable()

def renderTiles(envLLs, minz, maxz):
    if not hasattr(envLLs, '__iter__'):
        envLLs = (envLLs,)
    queue = Queue(32)
    renderers = {}
    for i in range(NUM_THREADS):
        renderer = RenderThread(queue, maxz, i)
        renderThread = threading.Thread(target=renderer.renderLoop)
        renderThread.start()
        renderers[i] = renderThread
    for envLL in envLLs:
        for z in range(minz, maxz+1):
            ntiles = NTILES[z]
            (fromx, tox, fromy, toy) = getTileRange(envLL, z, ntiles)
            for x in range(fromx, tox+1):
                for y in range(fromy, toy+1):
                    queue.put((z, x, y))
    for i in range(NUM_THREADS):
        queue.put(None)
    queue.join()
    for i in range(NUM_THREADS):
        renderers[i].join()       

def renderToPdf(envLL, filename, sizex, sizey):
    """Renders the specified Box2d and zoom level as a PDF"""
    basefilename = os.path.splitext(filename)[0]
    mergedpdf = None
    for mapname in MAPNIK_LAYERS:
        print 'Rendering', mapname
        # Render layer PDF.
        localfilename = basefilename + '_' + mapname + '.pdf';
        file = open(localfilename, 'wb')
        surface = cairo.PDFSurface(file.name, sizex, sizey) 
        envMerc = LLToMerc(envLL)
        map = mapnik.Map(sizex, sizey)
        mapnik.load_map(map, mapname + ".xml")
        map.zoom_to_box(envMerc)
        mapnik.render(map, surface)
        surface.finish()
        file.close()
        # Merge with master.
        if not mergedpdf:            
            mergedpdf = PdfFileWriter()
            localpdf = PdfFileReader(open(localfilename, "rb"))
            page = localpdf.getPage(0)
            mergedpdf.addPage(page)
        else:
            localpdf = PdfFileReader(open(localfilename, "rb"))
            page.mergePage(localpdf.getPage(0))
    output = open(filename, 'wb')
    mergedpdf.write(output)
    output.close()

def printSyntax():
    print "Syntax:"
    print " toposm.py render <area(s)> <minZoom> <maxZoom>"
    print " toposm.py prep <area(s)>"
    print " toposm.py info"
    print "Areas are named entities in areas.py."

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == 'render':
        areaname = sys.argv[2]
        minzoom = int(sys.argv[3])
        maxzoom = int(sys.argv[4])
        env = vars(areas)[areaname]            
        print "Render: %s %s, z: %d-%d" % (areaname, env, minzoom, maxzoom)
        BASE_TILE_DIR = path.join(BASE_TILE_DIR, areaname)
        renderTiles(env, minzoom, maxzoom)
    elif cmd == 'prep':
        areaname = sys.argv[2]
        env = vars(areas)[areaname]
        print "Prepare data: %s %s" % (areaname, env)
        prepareData(env)
    elif cmd == 'info':
        toposmInfo()
    else:
        printSyntax()
        sys.exit(1)
