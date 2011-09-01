#!/usr/bin/python

try:
    from mapnik2 import Box2d
except ImportError:
    from mapnik import Envelope as Box2d
    
# Misc test areas
WA = Box2d(-125.3, 45.4, -116.8, 49.1)
WAdetail = Box2d(-123.4, 46.2, -120.0, 48.1)
Seattle = Box2d(-122.4, 47.5, -122.2, 47.7)
WAnw = Box2d(-125.3, 47.7, -121, 49.1)
WAne = Box2d(-121, 47.7, -116.8, 49.1)
WAsw = Box2d(-125.3, 45.4, -121, 47.7)
WAse = Box2d(-121, 45.4, -116.8, 47.7)
NEdetail = Box2d(-71.5, 42, -70.5, 43)
Stow = Box2d(-71.55, 42.40, -71.46, 42.47)
BostonSS = Box2d(-71.2, 42.0, -70.6, 42.4)
BostonDetail = Box2d(-71.11, 42.30, -70.99, 42.41)
COdetail = Box2d(-105.1, 38.7, -104.7, 39.0)
COminor = Box2d(-105.0, 38.8, -104.8, 38.95)

NEdetail1 = Box2d(-71.0, 42.0, -70.5, 42.5)
NEdetail2 = Box2d(-71.0, 42.5, -70.5, 43.0)
NEdetail3 = Box2d(-71.5, 42.0, -71.0, 42.5)
NEdetail4 = Box2d(-71.5, 42.5, -71.0, 43.0)

ca = Box2d(-124.9, 32.3, -113.9, 42.1)
cadetail = Box2d(-123.4, 36.2, -118.0, 38.0)
oakland = Box2d(-122.34, 37.75, -122.12, 37.89)
yosdetail = Box2d(-119.67, 37.70, -119.52, 37.76)

# Main US zones
US = Box2d(-126, 24, -66, 56)
USnw = Box2d(-126, 40, -96, 56)
USne = Box2d(-96, 40, -66, 56)
USsw = Box2d(-126, 24, -96, 40)
USse = Box2d(-96, 24, -66, 40)

# US UTM Zones
UTM10S = Box2d(-126, 32, -120, 40)
UTM10T = Box2d(-126, 40, -120, 48)
UTM10U = Box2d(-126, 48, -120, 56)
UTM10 = [UTM10S, UTM10T, UTM10U]
UTM11R = Box2d(-120, 24, -114, 32)
UTM11S = Box2d(-120, 32, -114, 40)
UTM11T = Box2d(-120, 40, -114, 48)
UTM11U = Box2d(-120, 48, -114, 56)
UTM11 = [UTM11R, UTM11S, UTM11T, UTM11U]
UTM12R = Box2d(-114, 24, -108, 32)
UTM12S = Box2d(-114, 32, -108, 40)
UTM12T = Box2d(-114, 40, -108, 48)
UTM12U = Box2d(-114, 48, -108, 56)
UTM12 = [UTM12R, UTM12S, UTM12T, UTM12U]
UTM13R = Box2d(-108, 24, -102, 32)
UTM13S = Box2d(-108, 32, -102, 40)
UTM13T = Box2d(-108, 40, -102, 48)
UTM13U = Box2d(-108, 48, -102, 56)
UTM13 = [UTM13R, UTM13S, UTM13T, UTM13U]
UTM14R = Box2d(-102, 24, -96, 32)
UTM14S = Box2d(-102, 32, -96, 40)
UTM14T = Box2d(-102, 40, -96, 48)
UTM14U = Box2d(-102, 48, -96, 56)
UTM14 = [UTM14R, UTM14S, UTM14T, UTM14U]
UTM15R = Box2d(-96, 24, -90, 32)
UTM15S = Box2d(-96, 32, -90, 40)
UTM15T = Box2d(-96, 40, -90, 48)
UTM15U = Box2d(-96, 48, -90, 56)
UTM15 = [UTM15R, UTM15S, UTM15T, UTM15U]
UTM16R = Box2d(-90, 24, -84, 32)
UTM16S = Box2d(-90, 32, -84, 40)
UTM16T = Box2d(-90, 40, -84, 48)
UTM16U = Box2d(-90, 48, -84, 56)
UTM16 = [UTM16R, UTM16S, UTM16T, UTM16U]
UTM17R = Box2d(-84, 24, -78, 32)
UTM17S = Box2d(-84, 32, -78, 40)
UTM17T = Box2d(-84, 40, -78, 48)
UTM17U = Box2d(-84, 48, -78, 56)
UTM17 = [UTM17R, UTM17S, UTM17T, UTM17U]
UTM18R = Box2d(-78, 24, -72, 32)
UTM18S = Box2d(-78, 32, -72, 40)
UTM18T = Box2d(-78, 40, -72, 48)
UTM18U = Box2d(-78, 48, -72, 56)
UTM18 = [UTM18R, UTM18S, UTM18T, UTM18U]
UTM19R = Box2d(-72, 24, -66, 32)
UTM19S = Box2d(-72, 32, -66, 40)
UTM19T = Box2d(-72, 40, -66, 48)
UTM19U = Box2d(-72, 48, -66, 56)
UTM19 = [UTM19R, UTM19S, UTM19T, UTM19U]

# Cities / Metro areas
Boston = Box2d(-71.36, 42.13, -70.70, 42.60)
NewYorkCity = Box2d(-74.39, 40.50, -73.56, 41.11)
Philadelphia = Box2d(-75.43, 39.81, -74.88, 40.19)
WashingtonDC = Box2d(-77.33, 38.66, -76.79, 39.10)
Detroit = Box2d(-83.58, 42.04, -82.82, 42.71)
Chicago = Box2d(-88.54, 41.45, -87.29, 42.42)

Indianapolis = Box2d(-86.38, 39.61, -85.95, 39.97)
MinneapolisStPaul = Box2d(-93.72, 44.62, -92.65, 45.33)
DenverBoulderCoSprings = Box2d(-105.38, 38.66, -104.52, 40.13)
SaltLakeCityOgdenProvo = Box2d(-112.3, 40.05, -111.34, 41.4)
SeattlePugetOlympics = Box2d(-124.84, 46.91, -121.32, 48.56)
Portland = Box2d(-123.19, 45.17, -122.18, 45.89)
SanFranciscoBay = Box2d(-123.04, 36.93, -121.58, 38.19)

LosAngeles = Box2d(-120.07, 33.40, -116.88, 34.94)
SanDiego = Box2d(-117.47, 32.43, -116.83, 33.24)
Phoenix = Box2d(-112.75, 33.14, -111.43, 33.83)
LasVegas = Box2d(-115.39, 35.92, -114.69, 36.39)
SantaFe = Box2d(-106.15, 35.49, -105.76, 35.83)
Albuquerque = Box2d(-106.87, 34.89, -106.25, 35.34)
Houston = Box2d(-95.62, 29.53, -94.86, 29.96)

DallasFortWorth = Box2d(-97.60, 32.53, -96.47, 33.06)
SanAntonio = Box2d(-98.70, 29.27, -98.32, 29.59)
NewOrleans = Box2d(-90.64, 29.44, -89.59, 30.46)
Atlanta = Box2d(-84.64, 33.49, -84.11, 34.02)
Jacksonville = Box2d(-81.80, 30.11, -81.32, 30.48)
OrlandoTitusville = Box2d(-81.75, 27.96, -80.38, 28.91)
FloridaSE = Box2d(-80.65, 24.90, -79.99, 27.96)

Cities = [Boston, NewYorkCity, Philadelphia, WashingtonDC, Detroit,
    Chicago, Indianapolis, MinneapolisStPaul, DenverBoulderCoSprings,
    SaltLakeCityOgdenProvo, SeattlePugetOlympics, Portland,
    SanFranciscoBay, LosAngeles, SanDiego, Phoenix, LasVegas, SantaFe,
    Albuquerque, Houston, DallasFortWorth, SanAntonio, NewOrleans,
    Atlanta, Jacksonville, OrlandoTitusville, FloridaSE]


# Nature Areas
YellowstoneTetons = Box2d(-111.26, 43.50, -109.76, 45.13)
OregonCascades = Box2d(-123.26, 41.94, -119.88, 42.20)
SierraNevN = Box2d(-122.67, 38.72, -119.64, 42.07)
SierraNevC = Box2d(-121.35, 36.74, -116.88, 38.77)
SierraNevS = Box2d(-119.42, 35.29, -116.12, 36.79)

GrandCanyon = Box2d(-114.92, 35.70, -111.56, 36.93)
Zion = Box2d(-113.25, 37.12, -112.83, 37.52)
Bryce = Box2d(-112.31, 37.40, -112.03, 37.74)
ArchesCanyonlands = Box2d(-110.27, 37.92, -109.26, 38.88)
CapitolReef = Box2d(-111.45, 37.56, -110.82, 38.56)
MesaVerde = Box2d(-108.59, 37.12, -108.31, 37.37)
Glacier = Box2d(-114.51, 48.22, -113.21, 49.02)

RockyMountains = Box2d(-108.81, 35.84, -104.44, 40.94)
Acadia = Box2d(-68.48, 44.10, -68.11, 44.48)
GreatSmokyMountains = Box2d(-84.03, 35.41, -82.99, 35.80)
GuadulupeCarlsbad = Box2d(-105.2, 31.72, -104.21, 32.55)
MammothCave = Box2d(-86.40, 37.04, -85.87, 37.35)
NorthCascades = Box2d(-122.00, 48.18, -120.60, 49.01)
Badlands = Box2d(-102.98, 43.43, -101.79, 44.00)

BlackHills = Box2d(-104.78, 43.49, -103.21, 44.69)
GreatSandDunes = Box2d(-105.74, 37.64, -105.39, 37.95)
WhiteSands = Box2d(-106.84, 32.28, -105.34, 33.51)
GreenMountains = Box2d(-73.23, 43.81, -72.61, 44.76)
WhiteMountains = Box2d(-72.07, 43.73, -70.69, 44.78)
Adirondacks = Box2d(-75.40, 43.11, -73.35, 44.98)
EvergladesKeys = Box2d(-81.84, 24.50, -80.22, 25.91)
NiagaraFalls = Box2d(-79.43, 42.77, -78.66, 43.32)

Nature = [YellowstoneTetons, OregonCascades, SierraNevN,
    SierraNevC, SierraNevS, GrandCanyon, Zion, Bryce,
    ArchesCanyonlands, CapitolReef, MesaVerde, Glacier,
    RockyMountains, Acadia, GreatSmokyMountains,
    GuadulupeCarlsbad, MammothCave, NorthCascades, Badlands,
    BlackHills, GreatSandDunes, WhiteSands, GreenMountains,
    WhiteMountains, Adirondacks, EvergladesKeys, NiagaraFalls]

