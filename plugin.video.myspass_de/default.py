#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import time
import datetime
import YDStreamExtractor



import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])

args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
defaultBackground = ""
defaultThumb = ""
cliplist=[]
filelist=[]
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)

mainurl="http://www.myspass.de"
#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       
xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"



def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def parameters_string_to_dict(parameters):
  paramDict = {}
  if parameters:
    paramPairs = parameters[1:].split("&")
    for paramsPair in paramPairs:
      paramSplits = paramsPair.split('=')
      if (len(paramSplits)) == 2:
        paramDict[paramSplits[0]] = paramSplits[1]
  return paramDict
  
    
def addDir(name, url, mode, iconimage, desc=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  if useThumbAsFanart:
    if not iconimage or iconimage==icon or iconimage==defaultThumb:
      iconimage = defaultBackground    
    liz.setArt({ 'fanart': iconimage })
  else:
    liz.setArt({ 'fanart': defaultBackground })    
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
  
def addLink(name, url, mode, iconimage, duration="", desc="",artist_id="",genre="",shortname="",production_year=0,zeit=0,liedid=0):  
  cd=addon.getSetting("password")  
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre,"Sorttitle":shortname,"Dateadded":zeit,"year":production_year })
  liz.setProperty('IsPlayable', 'true')
  liz.addStreamInfo('video', { 'duration' : duration })
  liz.setArt({ 'fanart': iconimage })   
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
  return ok


def getUrl(url,data="x"):        
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Dalvik/2.1.0 (Linux; U; Android 5.0;)"
        opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        return content


      #addDir(namenliste[i], namenliste[i], mode+datum,logoliste[i],ids=str(idliste[i]))
   #xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)   
  



params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

def startpage(url):
   content=getUrl(url)
   struktur = json.loads(content) 
   for element in struktur["data"]:
       thumbnail=element["video"]["original_image"].replace("\/","/")
       sendung=element["format"]
       titel=element["title"]
       desc=element["video"]["teaser_text"]       
       staffel=element["video"]["season_number"]
       if len(staffel)==1:
         staffel="0"+staffel
       episode=element["video"]["episode_nr"]
       if len(episode)==1:
         episode="0"+episode       
       videourl=element["video"]["myspass_url"].replace("\/","/")
       laenge=element["video"]["play_length"]
       if " Teil "in titel:
         laenge=0
         titel = re.compile('(.+?) - Teil [0-9]+', re.DOTALL).findall(titel)[0]         
       name="S"+staffel+"E"+episode+" "+sendung +" - "+titel
       addDir(name,videourl,"playvideo","http:"+thumbnail,desc=desc)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def videos(url):
   content=getUrl(url)
   struktur = json.loads(content) 
   for element in struktur["data"]:
       thumbnail=element["original_image"].replace("\/","/")
       sendung=element["format"]
       titel=element["title"]
       desc=element["teaser_text"]       
       staffel=element["season_number"]
       if len(staffel)==1:
         staffel="0"+staffel
       episode=element["episode_nr"]
       if len(episode)==1:
         episode="0"+episode       
       videourl=element["myspass_url"].replace("\/","/")
       laenge=element["play_length"]
       if " Teil "in titel:
         laenge=0
         titel = re.compile('(.+?) - Teil [0-9]+', re.DOTALL).findall(titel)[0]
       name="S"+staffel+"E"+episode+" "+sendung +" - "+titel
       addDir(name,videourl,"playvideo","http:"+thumbnail,desc=desc)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
   
def shows(url):
   content=getUrl(url)
   struktur = json.loads(content) 
   for element in struktur["data"]:
    id=element["format_id"]
    desc=element["format_description"]
    logo=element["latestVideo"]["original_image"].replace("\/","/")
    name=element["format"]
    addDir(name, "http://m.myspass.de/api/index.php?command=seasonslist&id="+id, "show", "http:"+logo, desc=desc)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)    



def show(url):
   content=getUrl(url)
   struktur = json.loads(content) 
   for element in struktur["data"]:
     name=element["season_name"]
     desc=element["season_description"]
     id=element["season_id"]
     logo=element["latestVideo"]["original_image"].replace("\/","/")
     addDir(name, "http://m.myspass.de/api/index.php?command=seasonepisodes&id="+id, "videos", "http:"+logo, desc=desc)
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  

def NEXT(url):
 playlist = xbmc.PlayList(1)
 content=getUrl(url)
 urlnext=re.compile('<div class="full_episode_button desktop_only"><a href="(.+?)">', re.DOTALL).findall(content)[0]
 urlnext="http://www.myspass.de/myspass"+urlnext
 content=getUrl(urlnext)
 title=re.compile('"headline":"(.+?)",', re.DOTALL).findall(content)[0]
 desc=re.compile('"description":"(.+?)"', re.DOTALL).findall(content)[0]
 thumb=re.compile('"thumbnailUrl":"(.+?)"', re.DOTALL).findall(content)[0]
 debug("NEXTT URL :"+urlnext)
 vid = YDStreamExtractor.getVideoInfo(urlnext,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum        
 stream_url = vid.streamURL()            
 stream_url=stream_url.split("|")[0]
 u = base_url+"?url="+urllib.quote_plus(urlnext)+"&mode="+str("NEXT")
 listitem = xbmcgui.ListItem(path=u)
 playlist.add(u, listitem)  
 listitem = xbmcgui.ListItem(path=stream_url, iconImage="", thumbnailImage=thumb)
 listitem.setInfo(type="Video", infoLabels={"Title": title, "Plot": desc})  
 xbmcplugin.setResolvedUrl(addon_handle,True, listitem)
 
def playvideo(url)      :
        content=getUrl(url)        
        title=re.compile('"headline":"(.+?)",', re.DOTALL).findall(content)[0]
        desc=re.compile('"description":"(.+?)"', re.DOTALL).findall(content)[0]
        thumb=re.compile('"thumbnailUrl":"(.+?)"', re.DOTALL).findall(content)[0]
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear() 
        vid = YDStreamExtractor.getVideoInfo(url,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum        
        stream_url = vid.streamURL()            
        stream_url=stream_url.split("|")[0]
        debug("stream_url :"+stream_url)
        listitem = xbmcgui.ListItem(path=stream_url, iconImage="", thumbnailImage=thumb)
        listitem.setInfo(type="Video", infoLabels={"Title": title, "Plot": desc})  
        #listitem = xbmcgui.ListItem(path=stream_url)
        playlist.add(stream_url, listitem)  
        u = base_url+"?url="+urllib.quote_plus(url)+"&mode="+str("NEXT")
        listitem = xbmcgui.ListItem(path=u)
        playlist.add(u, listitem)  
        xbmc.Player().play(playlist)        
        #xbmcplugin.setResolvedUrl(addon_handle,True, listitem)

if mode is '':
    addDir("Home", "http://m.myspass.de/api/index.php?command=hometeaser", 'startpage',"")   
    addDir("Ganze Folgen", "http://m.myspass.de/api/index.php?command=formats", 'shows',"")   
    addDir("Shows A-Z", "http://m.myspass.de/api/index.php?command=azformats", 'shows',"")    
    addDir("Beliebteste", "http://m.myspass.de/api/index.php?command=favourite", 'videos',"")           
    addDir("Neueste", "http://m.myspass.de/api/index.php?command=latest&length=20", 'videos',"")           
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  if mode == 'startpage':
          startpage(url)
  if mode == 'shows':
          shows(url)
  if mode == 'show':
          show(url)          
  if mode == 'playvideo':
          playvideo(url)
  if mode == 'videos':
          videos(url)                                    
  if mode == 'NEXT' :
           NEXT(url)