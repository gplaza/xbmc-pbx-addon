
import urllib, os, re, urllib2
import xbmc, xbmcgui
import xml.dom.minidom

 
#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7

def DownloaderClass(url,dest):
    dp = xbmcgui.DialogProgress()
    dp.create("My Script","Downloading File",url)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        print percent
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        print "DOWNLOAD CANCELLED" # need to get this part working
        dp.close()

class MyClass(xbmcgui.Window):
  def __init__(self):
    self.strActionInfo = xbmcgui.ControlLabel(100, 120, 600, 400, '', 'font13', '0xFFFF00FF')
    self.addControl(self.strActionInfo)
    self.strActionInfo.setLabel('Push BACK to quit - A to select')
    self.list = xbmcgui.ControlList(200, 150, 300, 200)
    self.addControl(self.list)
    document = open(localfile,'r')
    dom = xml.dom.minidom.parse(document)
    document.close
    results = self.getWSResults(dom,"src")
    for result in results:
      self.list.addItem(result)
    dom.unlink()
    self.setFocus(self.list)

  def getWSResults(self, xmldoc, tag):
    results = []
    xmlNode = xmldoc.getElementsByTagName(tag)

    def getNodeResults(xmlNodeList):
        for node in xmlNodeList.childNodes:
            if node.hasChildNodes():
                getNodeResults(node)
            else:
                results.append(node.nodeValue)

    for nodeList in xmlNode:
        getNodeResults(nodeList)
    return results
 
  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU:
      self.close()

  def onControl(self, control):
    if control == self.list:
      item = self.list.getSelectedItem()
      self.message('You selected : ' + item.getLabel())  

  def message(self, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(" My message title", message)


ROOT_WD = os.getcwd().replace(";","")+"/"

webfile = 'http://asterisk/xbmc-pbx-addon.php'
localfile = ROOT_WD + 'cdr.xml'
DownloaderClass(webfile,localfile)

mydisplay = MyClass()
mydisplay .doModal()
del mydisplay

