# -*- coding: utf-8 -*

import re
import string
import cerealizer

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

class SVTSubMenu:
    def __init__(self):
        self.title = "SVT Play"
        self.thumb = R(THUMB)
        self.subitems = None
        self.xmlUrl = None
        
    def getMediaFunction(self):
        if self.subitems:
            return Function(DirectoryItem(GetSubMenu, title=self.title, thumb=self.thumb), title=self.title, subMenuList=self.subitems)
        else:
            return Function(DirectoryItem(GetRSSMenu, title=self.title, thumb=self.thumb), xmlUrl=self.xmlUrl)
            
class SVTRSSMenu:
    def __init__(self):
        self.title = ""
        self.thumb = R(THUMB)
        self.titleId = 0
        self.description = ""
        
    def getMediaFunction(self):
        return Function(DirectoryItem(GetVideoMenu, title=self.title, thumb=self.thumb, summary=self.description), titleId=self.titleId)
    
    
# Initializer called by the framework
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX,
                            MainMenu,
                            u"SVT Play 2",
                            "icon-default.png",
                            "art-default.jpg")
                            
    Plugin.AddViewGroup(name="List")
    HTTP.CacheTime = CACHE_TIME_SHORT
    HTTP.PreCache(URL_DEVICECONF)

    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(THUMB)
    VideoItem.thumb = R(THUMB)
    WebVideoItem.thumb = R(THUMB)
    
    cerealizer.register(SVTSubMenu)
    
def GetVideoMenu(sender):
    pass
    
def SVTRSSMenuFromContext(context):
    menu = SVTRSSMenu()
    menu.title = context.xpath('./title')[0].text
    menu.thumb = context.xpath('./media:content[@medium="image"]', namespaces=MEDIA_NS)[0].attrib["url"]
    menu.titleId = context.xpath('./svtplay:titleId', namespaces=SVTPLAY_NS)[0].text
    menu.description = context.xpath('./description')[0].text
    Log(menu.title, menu.thumb, menu.titleId)
    return menu
    
    
def GetRSSMenu(sender, xmlUrl):
    try:
        content = XML.ElementFromURL(xmlUrl, errors='ignore')
    except:
        return MessageContainer('Error', 'Unable to load title list')
    
    title = content.xpath('/rss/channel/title')[0].text
    Log(title)
    container = MediaContainer(viewGroup='List', title1=title)
    
    items = content.xpath('//item')
    for i in items:
        container.Append(SVTRSSMenuFromContext(i).getMediaFunction())
    
    return container
        
def GetSubNodesFromContext(context, type="rss"):
    nodes = []
    for subNode in context.xpath('./outline[@type="%s"]' % type):
        menu = SVTSubMenu()
        menu.title = subNode.attrib["text"]
        Log(subNode.attrib)
        if SVTPLAY_NS_TEXT+"thumbnail" in subNode.attrib:
            menu.thumb = subNode.attrib[SVTPLAY_NSS_TEXT+"thumbnail"]
        if "xmlUrl" in subNode.attrib:
            menu.xmlUrl = subNode.attrib["xmlUrl"]
        if len(subNode.getchildren()) > 0:
            menu.subitems = GetSubNodesFromContext(subNode)
        
        nodes.append(menu)
    return nodes
    
def GetSubMenu(sender, title, subMenuList):
    container = MediaContainer(viewGroup='List', title1=title)
    for node in subMenuList:
        container.Append(node.getMediaFunction())
    return container

def MainMenu():
    try:
        content = XML.ElementFromURL(URL_DEVICECONF, errors='ignore')
    except:
        return MessageContainer("Error", "Couldn't load mainmenu")
        
    m = content.xpath('//body')
    Log(m)
    nodeList = GetSubNodesFromContext(m[0], "menu")
    return GetSubMenu(None, "SVT Play", nodeList)
