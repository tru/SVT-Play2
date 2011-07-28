PLUGIN_PREFIX = "/video/svt2"
VERSION="1.0"

ART = "art-default.jpg"
THUMB = 'icon-default.png'

CACHE_TIME_LONG    = 60*60*24*30 # Thirty days
CACHE_TIME_SHORT   = 60*10    # 10  minutes
CACHE_TIME_1DAY    = 60*60*24
CACHE_TIME_SHOW = CACHE_TIME_1DAY
CACHE_TIME_EPISODE = CACHE_TIME_LONG

MEDIA_NS_TEXT = "http://search.yahoo.com/mrss/"
MEDIA_NS = {"media":MEDIA_NS_TEXT}
SVTPLAY_NS_TEXT = "http://xml.svtplay.se/ns/playrss"
SVTPLAY_NS = {"svtplay":SVTPLAY_NS_TEXT}
URL_DEVICECONF = "http://svtplay.se/mobil/deviceconfiguration.xml"

def GetThumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(THUMB))
