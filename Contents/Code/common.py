PLUGIN_PREFIX = "/video/svt2"
VERSION="1.0"

ART = "art-default.jpg"
THUMB = 'icon-default.png'

CACHE_TIME_LONG    = 60*60*24*30 # Thirty days
CACHE_TIME_SHORT   = 60*10    # 10  minutes
CACHE_TIME_1DAY    = 60*60*24
CACHE_TIME_SHOW = CACHE_TIME_1DAY
CACHE_TIME_EPISODE = CACHE_TIME_LONG

TYPE_DIR = "dir"
TYPE_VIDEO = "video"
TYPE_PROGRAM = "program"

MEDIA_NS_TEXT = "{http://search.yahoo.com/mrss/}"
MEDIA_NS = {"media":"http://search.yahoo.com/mrss/"}

SVTPLAY_RSS_NS_TEXT = "{http://xml.svtplay.se/ns/playrss}"
SVTPLAY_RSS_NS = {"svtplay":"http://xml.svtplay.se/ns/playrss"}

SVTPLAY_OPML_NS_TEXT = "{http://xml.svtplay.se/ns/playopml}"
SVTPLAY_OPML_NS = {"svtplay":"http://xml.svtplay.se/ns/playopml"}

OPENSEARCH_NS_TEXT = "{http://a9.com/-/spec/opensearch/1.1/}"
OPENSEARCH_NS = {"opensearch":"http://a9.com/-/spec/opensearch/1.1/"}

URL_DEVICECONF = "http://svtplay.se/mobil/deviceconfiguration.xml"
URL_VIDEO_LIST = "http://xml.svtplay.se/v1/video/list/"

def GetThumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(THUMB))
