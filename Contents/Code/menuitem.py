from common import *

class MenuItem:
    def __init__(self):
        self.title = None
        self.thumb = R(THUMB)
        self.subitems = None
        self.xmlUrl = None
        self.parent = None
        self.titleId = 0
        self.duration = 0
        self.description = None
        self.type = TYPE_DIR
        self.startIndex = 0

    def getMediaFunction(self):
        if (self.type == TYPE_DIR or self.type == TYPE_PROGRAM):
            Log("directory thumb = %s", self.thumb)

            return DirectoryObject(key=Callback(listMenu, menu=self),
                                   title=self.title,
                                   thumb=Callback(GetThumb, url=self.thumb))
        elif self.type == TYPE_VIDEO:
            return VideoClipObject(title=self.title,
                                    duration=int(self.duration),
                                    thumb=Callback(GetThumb, url=self.thumb),
                                    tagline=self.description,
                                    items = [
                                        MediaObject(
                                            parts = [PartObject(key=self.xmlUrl)],
                                            protocols = [Protocol.HTTPMP4Streaming],
                                            platforms = [ClientPlatform.iOS,
                                                         ClientPlatform.Android],
                                            video_codec = VideoCodec.H264,
                                            audio_codec = AudioCodec.AAC
                                        )
                                    ]
                                )

    def parseTeaserList(self, context):
        url = context.xpath('//svtplay:xmllink[@svtplay:type="title/list"]', namespaces=SVTPLAY_RSS_NS)
        if not url:
            Log("No match?")
            return None
        Log("HELLO: " + url[0].text)
        return self.xmlUrlList(url[0].text)

    def getVideoContext(self, context):
        videos = context.xpath(".//media:content", namespaces=MEDIA_NS)
        mp4 = None
        mp4bitrate = 0.0
        for v in videos:
            if v.attrib["type"] == 'video/mp4':
                if v.attrib["url"].startswith("rtmpe://"):
                    # we can't handle Encrypted shit.
                    continue
                if not ("bitrate" in v.attrib):
                    continue
                br = float(v.attrib["bitrate"])
                if br > mp4bitrate:
                    mp4bitrate = br
                    mp4 = v
            if v.attrib["type"] == 'application/vnd.apple.mpegurl':
                return v

        Log("No HLS, lets use mp4 with %f bitrate" % mp4bitrate)
        return mp4

    def parseList(self, context):
        retlist = []

        numberOfResults = int(context.xpath('/rss/channel/opensearch:totalResults',
                                            namespaces=OPENSEARCH_NS)[0].text)
        startIndex = int(context.xpath('/rss/channel/opensearch:startIndex',
                                       namespaces=OPENSEARCH_NS)[0].text)
        itemsPerPage = int(context.xpath('/rss/channel/opensearch:itemsPerPage',
                                         namespaces=OPENSEARCH_NS)[0].text)

        type = TYPE_VIDEO
        items = context.xpath('//item')
        for i in items:
            itemType = i.attrib[SVTPLAY_RSS_NS_TEXT+"type"]
            Log("itemType = %s", itemType)
            if (itemType == 'teaser'):
                return self.parseTeaserList(context)

            item = MenuItem()
            item.parent = self
            item.title = i.xpath('./title')[0].text
            thumbcontext = i.xpath('./media:thumbnail', namespaces=MEDIA_NS)
            if (thumbcontext) :
                item.thumb = thumbcontext[0].attrib["url"]

            # check type of the item
            if (itemType == "title"):
                item.type = TYPE_PROGRAM
                item.titleId = i.xpath('./svtplay:titleId',namespaces=SVTPLAY_RSS_NS)[0].text
                item.xmlUrl = URL_VIDEO_LIST+item.titleId
            elif (itemType == 'video'):
                item.type = TYPE_VIDEO

                videoContext = self.getVideoContext(i)
                if not videoContext:
                    Log("Skipped %s" % item.title)
                    continue

                item.xmlUrl = videoContext.attrib["url"]

                if "duration" in videoContext.attrib:
                    item.duration = int(videoContext.attrib["duration"]) * 1000
            else:
                Log("broken!")
                continue

            retlist.append(item)

        if (startIndex + itemsPerPage) < numberOfResults:
            Log("Adding next page, startIndex = %d" % (startIndex+itemsPerPage))
            item = MenuItem()
            item.parent = self
            item.title = u"Nästa sida"
            item.type = TYPE_DIR
            item.xmlUrl = self.xmlUrl
            item.startIndex = startIndex + itemsPerPage
            retlist.append(item)

        return retlist

    def xmlUrlList(self, url=None):
        if not url:
            url = self.xmlUrl

        # arguments
        args = []
        if self.startIndex > 0:
            args.append("start=%d" % self.startIndex)
        args.append("format=m3u8")
        url += "?%s" % ("&".join(args))
        Log("Requesting URL: %s" % url)

        try:
            context = XML.ElementFromURL(url, errors='ignore')
        except:
            return MessageContainer("Error", "Couldn't load mainmenu")

        return self.parseList(context)

def listMenu(menu=None):
    items = menu.subitems
    if not menu.subitems and menu.xmlUrl:
        items = menu.xmlUrlList()

    if items[0].type == TYPE_VIDEO:
        container = ObjectContainer(view_group='VideoGrid')
    elif items[0].type == TYPE_PROGRAM:
        container = ObjectContainer(view_group='ProgramList')
    else:
        container = ObjectContainer(view_group='List')

    if menu.parent:
            container.title1 = menu.parent.title
            container.title2 = menu.title
    else:
        container.title1 = menu.title

    for node in items:
        container.add(node.getMediaFunction())

    Log("listMenu contains %d subitems", len(items))
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

        thumbnailKey = SVTPLAY_OPML_NS_TEXT+"thumbnail"

        if thumbnailKey in subNode.attrib:
            menu.thumb = subNode.attrib[SVTPLAY_OPML_NS_TEXT+"thumbnail"]

        if "xmlUrl" in subNode.attrib:
            menu.xmlUrl = subNode.attrib["xmlUrl"]

        if len(subNode.getchildren()) > 0:
            menu.subitems = menuItemsFromContext(subNode, menu)

        nodes.append(menu)
    return nodes
