'''
        XBMC PBX Addon
               Script (GUI)

'''

import sys, os, os.path
import xbmc, xbmcgui

# Script constants
__scriptname__ = "XBMC PBX Addon"
__author__ = "hmronline"
__url__ = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__ = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__credits__ = "XBMC Team, py-Asterisk"
__version__ = "0.0.4"

xbmc.output(__scriptname__ + " Version: " + __version__  + "\n")
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(os.getcwd(),'resources','lib'))
sys.path.append(BASE_RESOURCE_PATH)

import urllib, urlparse, urllib2
import re, traceback, time
import xml.dom.minidom
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util

__language__ = xbmc.Language(os.getcwd()).getLocalizedString

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT_ITEM = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
ACTION_PAUSE = 12
ACTION_STOP = 13
ACTION_NEXT_ITEM = 14
ACTION_PREV_ITEM = 15
ACTION_EXIT_SCRIPT = (9, 10)

# check if build is special:// aware - set roots paths accordingly
XBMC_HOME = 'special://home'
if not os.path.isdir(xbmc.translatePath(XBMC_HOME)):
	# if fails to convert to Q:, old builds
        XBMC_HOME = 'Q:'

#############################################################################################################
def log(msg):
	try:
		xbmc.output("[%s]: %s\n" % (__scriptname__,msg))
	except:
		pass

#############################################################################################################
class MainGUI(xbmcgui.WindowXML):

	def __init__(self,*args,**kwargs):
		log("__init__()")
		xbmcgui.WindowXML.__init__(self,*args,**kwargs)

	#####################################################################################################
        def onInit(self):
		log("> onInit()")
		dialog = xbmcgui.DialogProgress()
		# Starting...
		dialog.create(__scriptname__,__language__(30061))
		# Fetching Asterisk Info...
		dialog.update(25,__language__(30063))
		self.getInfo()
		# Displaying Asterisk Info...
		dialog.update(50,__language__(30064))
		self.showInfo()
		# Done...
		dialog.update(100,__language__(30065))
		dialog.close()
		del dialog
		log(">> Done.")

	#####################################################################################################
	def getInfo(self):
		log("> getInfo()")
		settings = xbmc.Settings(path=os.getcwd())
		str_url = settings.getSetting("asterisk_info_url")
		str_url = str_url +"?vm&cdr&mailbox="+ settings.getSetting("asterisk_vm_mailbox")
		str_url = str_url +"&vmcontext="+ settings.getSetting("asterisk_vm_context")
		#log(">> " + str_url)
		f = urllib.urlopen(str_url)
		self.dom = xml.dom.minidom.parse(f)
		#log(self.dom.toxml())
		f.close()
		del f
		del settings

	#####################################################################################################
	def showInfo(self):
		log("> showInfo()")
		options = ["cdr","vm"]
		i = 120
		try:
			xbmcgui.lock()
			for option in options:
				self.getControl(i).reset()
				# Parse CDR/VM XML content
				for node in self.dom.getElementsByTagName(option):
					listitem = xbmcgui.ListItem()
					for childNode in node.childNodes:
						if (childNode.nodeName != "#text"):
							if (childNode.firstChild):
								listitem.setProperty(childNode.nodeName,childNode.firstChild.data)
							else:
								listitem.setProperty(childNode.nodeName,"")
					self.getControl(i).addItem(listitem)
					del listitem
				i = i + 1
			xbmcgui.unlock()
		except:
			log(">> ERROR: %s::%s (%d) - %s" % (self.__class__.__name__,sys.exc_info()[2].tb_frame.f_code.co_name,sys.exc_info()[2].tb_lineno,sys.exc_info()[1],))

	#####################################################################################################
	def onAction(self,action):
		#log("> onAction()")
		if (action in ACTION_EXIT_SCRIPT):
			self.close()

	def onClick(self,controlId):
		#log("> onClick(" + str(controlId) + ")")
		# Initiate outgoing call
		if (controlId == 120):
			number_to_call = self.getControl(120).getSelectedItem().getProperty("src")
			if (number_to_call != ""):
				dialog = xbmcgui.Dialog()
				if (dialog.yesno(__scriptname__,__language__(30104) + " '" + number_to_call + "'?")):
					self.make_outgoing_call(number_to_call)
				del dialog
		# Play Voice Mail
		elif (controlId == 121):
			recindex = self.getControl(121).getSelectedItem().getProperty("recindex")
			if (recindex != ""):
				dialog = xbmcgui.Dialog()
				if (dialog.yesno(__scriptname__,__language__(30105))):
					self.play_voice_mail(recindex)
				del dialog
		# Settings
		elif (controlId == 115):
			settings = xbmc.Settings(path=os.getcwd())
			settings.openSettings()
			del settings
			self.onInit()

	def onFocus(self,controlId):
		pass

	#####################################################################################################
	def make_outgoing_call(self,number_to_call):
		log("> make_outgoing_call()")
		settings = xbmc.Settings(path=os.getcwd())
		manager_host_port = settings.getSetting("asterisk_manager_host"),int(settings.getSetting("asterisk_manager_port"))
		pbx = Manager(manager_host_port,settings.getSetting("asterisk_manager_user"),settings.getSetting("asterisk_manager_pass"))
        	pbx.Originate(settings.getSetting("asterisk_outbound_extension"),settings.getSetting("asterisk_outbound_context"),number_to_call,1)
		del pbx
		del settings
		log(">> Done.")

	#####################################################################################################
	def play_voice_mail(self,recindex):
		log("> play_voice_mail()")
		settings = xbmc.Settings(path=os.getcwd())
		audio_format = ["wav","gsm","mp3"]
		asterisk_vm_format = audio_format[int(settings.getSetting("asterisk_vm_format"))]
		url_vm = settings.getSetting("asterisk_info_url") +"?recindex="+ recindex
		url_vm = url_vm +"&mailbox="+ settings.getSetting("asterisk_vm_mailbox")
		url_vm = url_vm +"&vmcontext="+ settings.getSetting("asterisk_vm_context")
		url_vm = url_vm +"&format="+ asterisk_vm_format
		xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)
		xbmc_player.play(url_vm)
		del xbmc_player
		del settings


#############################################################################################################
class FirstTimeGUI(xbmcgui.Window):

	def __init__(self):
		log("__init__()")
		dialog = xbmcgui.ControlTextBox(1,1,600,600,"font12","0xFFFFFFFF")
		msg = ""
		for i in range(1,10):
			msg = msg + __language__(30000 + i) + "\n"
		self.addControl(dialog)
		dialog.setText(msg)
		log(">> Done.")

	#####################################################################################################
	def onAction(self,action):
		#log("> onAction()")
		settings = xbmc.Settings(path=os.getcwd())
		settings.openSettings()
		del settings
		self.close()



#################################################################################################################
 # Starts here
#################################################################################################################

log("XBMC_HOME=%s" % XBMC_HOME)

try:
	log("Launching GUI...")
	settings = xbmc.Settings(path=os.getcwd())
	first_time_use = settings.getSetting("first_time_use")
	settings.setSetting("first_time_use","false")
	del settings
	if (first_time_use == "true"):
		ui = FirstTimeGUI()
	else:
		ui = MainGUI("script_xbmc-pbx-addon_main.xml",os.getcwd(),"Default")
	ui.doModal()
except:
	xbmc_notification = str(sys.exc_info()[1])
	log(">> " + xbmc_notification)
	xbmc.executebuiltin("XBMC.Notification("+ __language__(30051) +","+ xbmc_notification +","+ str(15*1000) +")")
try:
	del ui
	self.dom.unlink()
	del self.dom
	sys.modules.clear()
except:
	pass

