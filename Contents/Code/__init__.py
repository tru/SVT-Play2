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
                            THUMB,
                            ART)
                            
    Plugin.AddViewGroup(name='VideoGrid', viewMode='Episodes', mediaType='videos')
    Plugin.AddViewGroup(name='ProgramList', viewMode='Episodes', mediaType='videos')
    Plugin.AddViewGroup(name='List', viewMode='List', mediaType='videos')
    #HTTP.CacheTime = CACHE_TIME_SHORT
    #HTTP.PreCache(URL_DEVICECONF)

    ObjectContainer.title1 = "SVT Play"
    ObjectContainer.art = R(ART)
    DirectoryObject.thumb = R(THUMB)
    VideoClipObject.thumb = R(THUMB)
    
    cerealizer.register(menuitem.MenuItem)
    

def MainMenu():
    """
    m = ObjectContainer(view_group="List")    
    m.add(VideoClipObject(
        title = "test",
        items = [
          MediaObject(
            parts = [
              PartObject(key="http://www0.c90910.dna.qbrick.com/90910/od/20110727/svt_gavl_2011-07-27_221459_222501-hts-a-v1/svt_gavl_2011-07-27_221459_222501-hts-a-v1_vod.m3u8")
            ],
            protocols = [Protocol.HTTPMP4Streaming],
            platforms = [ClientPlatform.iOS, ClientPlatform.Android],
            video_codec = VideoCodec.H264,
            audio_codec = AudioCodec.AAC
          )]))
        

        
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
    
    return listMenu(rootMenu)
