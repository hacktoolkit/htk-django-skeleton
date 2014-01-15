import pygeoip

from libraries.geoip.constants import *

def get_geoip_country():
    gi_country = pygeoip.GeoIP(GEOIP_COUNTRY_DB, pygeoip.MEMORY_CACHE)
    return gi_country

def get_geoip_city():
    gi_city = pygeoip.GeoIP(GEOIP_CITY_DB, pygeoip.MEMORY_CACHE)
    return gi_city
