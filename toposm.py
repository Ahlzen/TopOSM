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

# Use mapnik2 if available, mapnik otherwise.
try:
    import mapnik2 as mapnik
    from mapnik2 import Coord, Box2d
except ImportError:
    import mapnik
    from mapnik import Coord
    from mapnik import Envelope as Box2d
print "Using mapnik version:", mapnik.mapnik_version()
if not mapnik.has_cairo():
    print "ERROR: Your mapnik does not have Cairo support."
    sys.exit(1)

from env import *
from coords import *
from common import *
import NED
import areas
from JobManager import JobManager

__author__      = "Lars Ahlzen and contributors"
__copyright__   = "(c) Lars Ahlzen and contributors 2008-2011"
__license__     = "GPLv2"


##### Render settings

# Set to true to save intermediate layers that are normally
# merged. Primarily useful for debugging and style editing.
SAVE_INTERMEDIATE_TILES = True

# If true, a composite JPEG layer is saved along with
# the standard PNG.
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

    #def renderTopoMetaTile(self, z, x, y, ntiles):
    #    for mapname in ['hillshade', 'colormap']:    
    #        msg = "Rendering %s %s %s %s" % (mapname, z, x, y)
    #        self.runAndLog(msg, renderTopoMetaTile, (z, x, y, ntiles, mapname))
            
    def renderMetaTile(self, z, x, y):
        ntiles = NTILES[z]
        if (z != self.currentz):
            self.init_zoomlevel(z)
        if not (allConstituentTilesExist(z, x, y, ntiles)):
            msg = "Rendering meta tile %s %s %s (%sx%s)" % \
                (z, x, y, ntiles, ntiles)
            self.runAndLog(msg, renderMetaTile, (z, x, y, ntiles, \
                self.maps['hypsorelief'], \
                self.maps['landcoverrelief'], \
                self.maps['areas'], \
                self.maps['ocean'], \
                self.maps['contours'], \
                self.maps['features']))

    #def combineAndSliceTopoMetaTile(self, z, x, y, ntiles):
    #    msg = "Combining topo tiles %s %s %s" % (z, x, y)
    #    layers = (('color-relief', '.jpg'),)
    #    self.runAndLog(msg, combineAndSlice, (z, x, y, ntiles, \
    #        './combine-color-relief-tiles', layers))

    #def combineAndSliceMapnikMetaTile(self, z, x, y, ntiles):
    #    msg = "Combining mapnik tiles %s %s %s" % (z, x, y)
    #    layers = (('contours', '.png'), ('features', '.png'))
    #    self.runAndLog(msg, combineAndSlice, (z, x, y, ntiles, \
    #        './combine-mapnik-tiles', layers))
    
    #def mergeTopoTiles(self, z, x, y, ntiles):
    #    for dx in range(x*ntiles, (x+1)*ntiles):
    #        for dy in range(y*ntiles, (y+1)*ntiles):
    #            if not tileExists('color-relief', z, dx, xy, '.jpg'):
    #                msg = "Merging topo tiles %s %s %s" % (z, x, y)
    #                self.runAndLog(msg, mergeSubtiles, \
    #                    (z, x, y, 'color-relief'))
                    
    #def createJpegTiles(self, z, x, y, quality, ntiles):
    #    for dx in range(x*ntiles, (x+1)*ntiles):
    #        for dy in range(y*ntiles, (y+1)*ntiles):
    #            if not tileExists('jpeg' + str(quality), z, dx, dy, '.jpg'):
    #                msg = "Creating JPEG%s %s %s %s" % (quality, z, dx, dy)
    #                self.runAndLog(msg, createJpegTile, (z, dx, dy, quality))
            
    def renderLoop(self):
        self.currentz = 0
        while True:
            r = self.q.get()
            if (r == None):
                self.q.task_done()
                break
            self.renderMetaTile(*r)
            self.q.task_done()

#    def render(self, z, x, y):
#        
#        self.renderMetaTile(z, x, y, ntiles[z])
            #self.renderMapnikMetaTile(z, x, y, ntiles)
            #self.combineAndSliceMapnikMetaTile(z, x, y, ntiles)
            #if z == self.maxz or \
            #    not allConstituentTopoTilesExist(z, x, y, ntiles):
            #    self.renderTopoMetaTile(z, x, y, ntiles)
            #    self.combineAndSliceTopoMetaTile(z, x, y, ntiles)
            #else:
            #    self.mergeTopoTiles(z, x, y, ntiles)
            #self.createJpegTiles(z, x, y, JPEG_QUALITY, ntiles)


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
    
#def allConstituentTopoTilesExist(z, x, y, ntiles):
#    subx = ntiles * x
#    suby = ntiles * y
#    return allTilesExist('color-relief', z+1, \
#        2*subx, 2*(subx+ntiles)-1, 2*suby, 2*(suby+ntiles)-1)
        
def allConstituentTilesExist(z, x, y, ntiles):
    fromx = x*ntiles
    tox = (x+1)*ntiles - 1
    fromy = y*ntiles
    toy = (y+1)*ntiles - 1
    # NOTE: This only checks for the final "composite" tile set...
    return allTilesExist('composite', z, fromx, tox, fromy, toy, 'png')
#    return \
#        allTilesExist('base', z, fromx, tox, fromy, toy, 'png') and \
#        allTilesExist('contours', z, fromx, tox, fromy, toy, 'png') and \
#        allTilesExist('features', z, fromx, tox, fromy, toy, 'png') and \
#        allTilesExist('composite', z, fromx, tox, fromy, toy, 'png') and \
#        allTilesExist('jpeg90', z, fromx, tox, fromy, toy, 'png')

def renderMetaTile(z, x, y, ntiles, hypsoreliefMap, landcoverreliefMap, areasMap, oceanMap, contoursMap, featuresMap):
    """Renders the specified map tile and saves the result (including the
    composite) as individual tiles."""
    hypsorelief = renderLayer('hypsorelief', z, x, y, ntiles, hypsoreliefMap, 'png')
    landcoverrelief = renderLayer('landcoverrelief', z, x, y, ntiles, landcoverreliefMap, 'png')
    areas = renderLayer('areas', z, x, y, ntiles, areasMap, 'png')
    ocean = renderLayer('ocean', z, x, y, ntiles, oceanMap, 'png', True)
    contours = renderLayer('contours', z, x, y, ntiles, contoursMap, 'png', True)
    features = renderLayer('features', z, x, y, ntiles, featuresMap, 'png', True)
    base_h = getComposite((hypsorelief, areas, ocean))
    base_l = getComposite((landcoverrelief, ocean))
    composite_h = getComposite((base_h, contours, features))
    composite_l = getComposite((base_l, contours, features))
    saveTiles(z, x, y, ntiles, 'base_h', base_h)
    saveTiles(z, x, y, ntiles, 'base_l', base_l)
    saveTiles(z, x, y, ntiles, 'contours', contours)
    saveTiles(z, x, y, ntiles, 'composite_h', composite_h)
    saveTiles(z, x, y, ntiles, 'composite_l', composite_l)
    saveTiles(z, x, y, ntiles, 'features', features)
    if SAVE_JPEG_COMPOSITE:
        basename = 'jpeg' + str(JPEG_COMPOSITE_QUALITY)
        saveTiles(z, x, y, ntiles, basename + '_h', composite_h, 'jpg', basename)
        saveTiles(z, x, y, ntiles, basename + '_l', composite_l, 'jpg', basename)
    if SAVE_INTERMEDIATE_TILES:
        saveTiles(z, x, y, ntiles, 'hypsorelief', hypsorelief)
        saveTiles(z, x, y, ntiles, 'landcoverrelief', landcoverrelief)
        saveTiles(z, x, y, ntiles, 'areas', areas)
        saveTiles(z, x, y, ntiles, 'ocean', ocean)
    
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

#    file = open(filename, 'wb')
#    surface = cairo.PDFSurface(file.name, sizex, sizey) 
#    envMerc = LLToMerc(envLL)

    # Combine all maps into one, since mapnik can't render
    # a single-page PDF otherwise.
#    comboMap = mapnik.Map(sizex, sizey)
#    for mapname in MAPNIK_LAYERS:
#        map = mapnik.Map(sizex, sizey)
#        mapnik.load_map(map, mapname + ".xml")
#        for layer in map.layers:
#           for stylename in layer.styles:
#                print 'adding style', stylename
#                comboMap.append_style(stylename, map.find_style(stylename))
#            comboMap.layers.append(layer)
#        #comboMap.layers.extend(map.layers)
#    comboMap.zoom_to_box(envMerc)
#    print "Scale:", comboMap.scale()
#    mapnik.render(comboMap, surface)
#    surface.finish()
   
#    for mapname in MAPNIK_LAYERS:
#        print "Rendering:", mapname
#        map = mapnik.Map(sizex, sizey)
#        mapnik.load_map(map, mapname + ".xml")
#        map.zoom_to_box(envMerc)
#        print "Scale:", map.scale()
#        mapnik.render(map, surface)
#    surface.finish()


    
#def renderMapnikMetaTile(z, x, y, ntiles, mapname, map):
#    env = getMercTileEnv(z, x, y, ntiles, True)
#    tilesize = getTileSize(ntiles, True)
#    if not metaTileExists(mapname, z, x, y, '.png'):
#        map.zoom_to_box(env)
#        image = mapnik.Image(tilesize, tilesize)
#        mapnik.render(map, image)
#        view = image.view(BORDER_WIDTH, BORDER_WIDTH, tilesize, tilesize)
#        ensureDirExists(getMetaTileDir(mapname, z))
#        view.save(getMetaTilePath(mapname, z, x, y, '.png'))

#def renderTopoMetaTile(z, x, y, ntiles, mapname):
#    env = getMercTileEnv(z, x, y, ntiles, False)
#    envLL = getLLTileEnv(z, x, y, ntiles, False)
#    destdir = getMetaTileDir(mapname, z)
#    # NOTE: gdalwarp won't save as png directly, hence this "hack"
#    destTilePath = getMetaTilePath(mapname, z, x, y, '.tif')
#    finalTilePath = getMetaTilePath(mapname, z, x, y, '.png')
#    if os.path.isfile(finalTilePath):
#        pass
#    else:
#        ensureDirExists(destdir)
#        nedSlices = NED.getSlices(mapname, envLL, '.png')
#        tilesize = getTileSize(ntiles, False)
#        if len(nedSlices) > 0:
#            cmd = 'gdalwarp -q -t_srs "%s" -te %f %f %f %f -ts %d %d -r lanczos -dstnodata 255 ' % \
#                (MERCATOR_PROJECTION_DEF, env.minx, env.miny, env.maxx, env.maxy, tilesize, tilesize)
#            for slice in nedSlices:
#                cmd = cmd + '"' + slice + '" '
#            cmd = cmd + '"' + destTilePath + '"'
#            os.system(cmd)
#            # convert to png and remove tif (to conserve space)
#            cmd = 'convert "%s" "%s" && rm "%s"' % \
#                (destTilePath, finalTilePath, destTilePath)
#            os.system(cmd)
#        else:
#            return False
#    return True

#def sliceMetaTile(z, x, y, ntiles, mapname, destSuffix = '.png'):
#    srcTilePath = getMetaTilePath(mapname, z, x, y, '.png')
#    for dx in range(0, ntiles):
#        destDir = path.join(getMetaTileDir(mapname, z), str((x*ntiles)+dx))
#        ensureDirExists(destDir)
#        for dy in range(0, ntiles):
#            destfile = path.join(destDir, str((y*ntiles)+dy) + destSuffix)
#            if not path.isfile(destfile):
#                offsetx = dx * TILE_SIZE
#                offsety = dy * TILE_SIZE
#                cmd = 'convert "%s" -crop %dx%d+%d+%d +repage "%s"' % \
#                    (srcTilePath, TILE_SIZE, TILE_SIZE, offsetx, offsety, \
#                     path.join(destDir, str((y*ntiles)+dy) + destSuffix))
#                os.system(cmd)
#            else:
#                pass
#    tryRemove(srcTilePath)

#def combineAndSlice(z, x, y, ntiles, script, namesAndExts):
#    allExist = True
#    for n in namesAndExts:
#        if not allTilesExist(n[0], z, x*ntiles, (x+1)*ntiles-1, \
#            y*ntiles, (y+1)*ntiles-1, n[1]):
#            allExist = False
#            break
#    if not allExist:
#        cmd = "%s %s %d %d %d %d" % \
#            (script, BASE_TILE_DIR, z, x, y, getTileSize(ntiles, False))
#        os.system(cmd)
#        for n in namesAndExts:
#            sliceMetaTile(z, x, y, ntiles, n[0], n[1])

#def mergeSubtiles(z, x, y, mapname, suffix = '.jpg'):
#    """Merges (up to) four subtiles from the next higher
#    zoom level into one subtile at the specified location"""
#    cmd = 'convert -size 512x512 xc:white'
#    for dx in range(0,2):
#        for dy in range(0,2):
#            srcx = x*2 + dx
#            srcy = y*2 + dy
#            srcpath = getTilePath(mapname, z+1, srcx, srcy, suffix)
#            if os.path.isfile(srcpath):
#                cmd = cmd + ' "' + srcpath + '"'
#                cmd = cmd + ' -geometry +' + str(dx*256) + '+' + str(dy*256)
#                cmd = cmd + ' -composite'
#    cmd = cmd + ' -scale 256x256'
#    ensureDirExists(getTileDir(mapname, z, x))
#    destpath = getTilePath(mapname, z, x, y, suffix)
#    cmd = cmd + ' "' + destpath + '"'
#   os.system(cmd)

# NOTE: This should be obsolete once all the issues with the
# raster layers are sorted out...
#def createJpegTile(z, x, y, quality):
#    colorreliefsrc = getTilePath('color-relief', z, x, y, '.jpg')
#    contourssrc = getTilePath('contours', z, x, y, '.png')
#    featuressrc = getTilePath('features', z, x, y, '.png')
#    desttile = getTilePath('jpeg' + str(quality), z, x, y, '.jpg')
#    if path.isfile(colorreliefsrc) and path.isfile(featuressrc):
#        ensureDirExists(path.dirname(desttile))        
#        # PIL generates internal errors opening the JPEG
#        # tiles so it's back to ImageMagick for now...
#        cmd = "convert " + colorreliefsrc;
#        if path.isfile(contourssrc):
#            cmd = cmd + " " + contourssrc + " -composite"
#       cmd = cmd + " " + featuressrc + " -composite"
#        cmd = cmd + " -quality " + str(quality) + " -strip " + desttile
#        os.system(cmd)
 

##### Public methods

def prepareData(envLLs):
    if not hasattr(envLLs, '__iter__'):
        envLLs = (envLLs,)
    manager = JobManager()
    for envLL in envLLs:
        tiles = NED.getTiles(envLL)        
        for tile in tiles:
            manager.addJob("Preparing %s" % (tile[0]), NED.prepDataFile, tile)
    manager.finish()
    
    console.printMessage("Converting m to ft")
    templ = 'echo "UPDATE %s SET height_ft = CAST(height * 3.28085 AS INT) ' \
        + 'WHERE height_ft IS NULL;" | psql -q "%s"'
    cmd = templ % (CONTOURS_TABLE, DATABASE)
    os.system(cmd)
    
    # NOTE: This removes a LOT of artifacts around shorelines. Unfortunately,
    # it also removes any legitimate 0ft contours (which may exist around
    # areas below sea-level).
    # TODO: Find a better workaround.
    console.printMessage('Removing sea-level contours')
    templ = 'echo "DELETE FROM %s WHERE height_ft = 0;" | psql -q "%s"'
    cmd = templ % (CONTOURS_TABLE, DATABASE)
    os.system(cmd)

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
    print "Areas are named entities in areas.py."

if __name__ == "__main__":
    try:
        if sys.argv[1] == 'render':
            areaname = sys.argv[2]
            minzoom = int(sys.argv[3])
            maxzoom = int(sys.argv[4])
            env = vars(areas)[areaname]            
            print "Render: %s %s, z: %d-%d" % (areaname, env, minzoom, maxzoom)
            BASE_TILE_DIR = path.join(BASE_TILE_DIR, areaname)
            renderTiles(env, minzoom, maxzoom)
        elif sys.argv[1] == 'prep':
            areaname = sys.argv[2]
            env = vars(areas)[areaname]
            print "Prepare data: %s %s" % (areaname, env)
            prepareData(env)
        else:
            raise Exception()
    except:
        printSyntax()
        sys.exit(1)
    
