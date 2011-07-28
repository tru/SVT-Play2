from common import *

class MenuItem:
    def __init__(self):
        self.title = None
        self.thumb = R(THUMB)
        self.subitems = None
        self.xmlUrl = None
        self.parent = None
        self.titleId = 0
        self.description = ""

    def getMediaFunction(self):            
        return Function(DirectoryItem(listMenu, title=self.title, thumb=self.thumb), menu=self)
        
        
    def parseTeaserList(self, context):
        return None
    
    def getVideoContext(self, context):
        videos = context.xpath(".//media:content", namespaces=MEDIA_NS)
        for v in videos:
            if v.attrib["type"] == 'application/vnd.apple.mpegurl':
                return v
        return None
    
    def parseVideoList(self, context):
    
        title = context.xpath('/rss/channel/title')[0].text
        dir = MediaContainer(title=title)
        items = context.xpath('//item[@svtplay:type="video"]', namespaces=SVTPLAY_NS)
        for i in items:
            videoTitle = i.xpath('./title')[0].text
            videoThumb = i.xpath('./media:thumbnail', namespaces=MEDIA_NS)[0].attrib["url"]

            videoContext = self.getVideoContext(i)
            videoURL = self.getRealURL(videoContext.attrib["url"])
            if not videoURL:
                continue
            
            if "duration" in videoContext.attrib:
                videoDuration = videoContext.attrib["duration"]
            else:
                videoDuration = 0
            
            dir.Append(VideoItem(videoURL, title=videoTitle, videoThumb=GetThumb(videoThumb), duration=videoDuration))
        
        return dir
        
    def getRealURL(self, url):
        Log("getting m3u8 file: %s", url)
        try:
            data = HTTP.Request(url, cacheTime=CACHE_TIME_1DAY).content
        except:
            return None
        lines = data.split('\n')
        layers = {}
        for l in lines:
            if not l.startswith('#EXT-X-STREAM-INF'):
                continue
            b = int(l[l.rfind('=')+1:])
            layers[b] = lines[lines.index(l)+1]
            
        high = max(layers.keys())
        
        Log("using %d", high)
        
        return layers[high]
        
    def xmlUrlList(self):
        try:
            context = XML.ElementFromURL(self.xmlUrl, errors='ignore')
        except:
            return MessageContainer("Error", "Couldn't load mainmenu")
            
        # need to figure out what we are dealing with here
        ismenu = context.xpath('/rss/channel/svtplay:listType', namespaces=SVTPLAY_NS)
        if ismenu:
            if ismenu[0].text == 'pgmMenu':
                Log("teaserList")
                return self.parseTeaserList(context)
            else:
                Log("don't handle this listtype")
        else:
            # videolist then?
            Log("videoList?")
            return self.parseVideoList(context)
            
        return None
    
def listMenu(sender, menu):
    if not menu.subitems and menu.xmlUrl:
        return menu.xmlUrlList()

    container = MediaContainer(viewGroup='List')

    if menu.parent:
            container.title1 = menu.parent.title
            container.title2 = menu.title
    else:
        container.title1 = menu.title
    
    for node in menu.subitems:
        container.Append(node.getMediaFunction())
    
    Log("listMenu contains %d subitems", len(menu.subitems))
    return container

def menuItemsFromContext(context, parent, type='rss'):
    nodes = []
    for subNode in context.xpath('./outline[@type="%s"]' % type):
        menu = MenuItem()
        menu.parent = parent
        menu.title = subNode.attrib["text"]
        if menu.title == "Hjälpmeny" or menu.title == "Sök":
            continue
#        Log("subitem = %s, parent %s", menu.title, menu.parent.title)
        if SVTPLAY_NS_TEXT+"thumbnail" in subNode.attrib:
            menu.thumb = subNode.attrib[SVTPLAY_NSS_TEXT+"thumbnail"]
        if "xmlUrl" in subNode.attrib:
            menu.xmlUrl = subNode.attrib["xmlUrl"]
        if len(subNode.getchildren()) > 0:
            menu.subitems = menuItemsFromContext(subNode, menu)
        
        nodes.append(menu)
    return nodes
