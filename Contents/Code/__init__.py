# -*- coding: utf-8 -*

import re
import string
import cerealizer

from common import *
import menuitem
from menuitem import listMenu
                
# Initializer called by the framework
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX,
                            MainMenu,
                            u"SVT Play 2",
                            "icon-default.png",
                            "art-default.jpg")
                            
    Plugin.AddViewGroup(name="List")
    #HTTP.CacheTime = CACHE_TIME_SHORT
    #HTTP.PreCache(URL_DEVICECONF)

    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(THUMB)
    VideoItem.thumb = R(THUMB)
    
    cerealizer.register(menuitem.MenuItem)
    

def MainMenu():
    """
    m = MediaContainer(title="test")
    m.Append(VideoItem("http://www0.c90910.dna.qbrick.com/90910/od/20110727/svt_gavl_2011-07-27_221459_222501-hts-a-v1/svt_gavl_2011-07-27_221459_222501-hts-a-v1_Layer5_vod.m3u8", title="test"))
    return m
    """ 
    try:
        context = XML.ElementFromURL(URL_DEVICECONF, errors='ignore')
    except:
        return MessageContainer("Error", "Couldn't load mainmenu")
        
    m = context.xpath('//body')
    
    rootMenu = menuitem.MenuItem()
    rootMenu.title = "SVT Play"
    rootMenu.subitems = menuitem.menuItemsFromContext(m[0], rootMenu, "menu")
    
    return listMenu(None, rootMenu)