import os
from configparser import ConfigParser


path = "/home/clifford/.config/roax/config"

config = ConfigParser()
config.read(path)
lat = config.get('HOME','lat')
lon = config.get('HOME','lon')
buffer = config.get('HOME','buffer')
print "Home location is at: ", lat, lon
print "Distance from home:  ", buffer

