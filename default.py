'''
        XBMC PBX Addon
               Script 

'''

import sys, os, os.path
import xbmc, xbmcgui

# Script constants
__scriptname__ = "XBMC PBX Addon"
__author__ = "hmronline"
__url__ = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__ = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__credits__ = "XBMC Team, py-Asterisk"
__version__ = "0.0.1"

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
class get_incoming_call(object):

        def __init__(self):
		log("__init__()")
                global xbmc_player
                xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		self.xbmc_player_paused = False
                self.ast_uniqid = 0
                self.events = Asterisk.Util.EventCollection()
                self.events.clear()
                self.events.subscribe('Newchannel',self.Newchannel)
                self.events.subscribe('NewCallerid',self.NewCallerid)
                self.events.subscribe('Hangup',self.Hangup)

	#####################################################################################################
        def Newchannel(self,pbx,event):
		#log("> NewChannel()")
		#log(">> " + event.Uniqueid)
		#log(">> " + event.ChannelStateDesc)
		# May use "Down" or "Ring" state.
		arr_chan_states = ['Down','Ring']
		asterisk_chan_state = str(arr_chan_states[int(settings.getSetting("asterisk_chan_state"))])
                if (event.ChannelStateDesc == asterisk_chan_state and self.ast_uniqid == 0):
                        self.ast_uniqid = event.Uniqueid
			#log(">> " + self.ast_uniqid)
			#log(">> " + asterisk_chan_state)

	#####################################################################################################
        def NewCallerid(self,pbx,event):
		#log("> NewCallerid()")
		#log(">> " + event.Uniqueid)
		#log(">> " + event.CallerIDName + " <" + event.CallerIDNum + ">")
                if (event.Uniqueid == self.ast_uniqid and event.CallerIDName != "" and event.CallerIDNum != ""):
                        self.newcall_actions(event)

	#####################################################################################################
        def Hangup(self,pbx,event):
		#log("> Hangup()")
		#log(">> " + event.Uniqueid)
                if (event.Uniqueid == self.ast_uniqid):
                        self.ast_uniqid = 0
                        self.hangup_actions(event)

	#####################################################################################################
        def hangup_actions(self,event):
                log("> hangup_actions()")
                if (xbmc_player.isPlaying() == 1):
			# Resume media
			xbmc_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
			time.sleep(1)
			xbmc_new_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
			if (self.xbmc_player_paused and xbmc_remaining_time == xbmc_new_remaining_time):
				log(">> Resume media...")
                        	xbmc_player.pause()
				self.xbmc_player_paused = False

	#####################################################################################################
        def newcall_actions(self,event):
		log("> newcall_actions()")
		log(">> Channel: " + str(event.Channel))
		#log(">> Unique ID: " + self.ast_uniqid)
                str_callerid = str(event.CallerIDName + " <"+ event.CallerIDNum +">")
                log(">> CallerID: " + str_callerid)
                if (xbmc_player.isPlaying() == 1):
                        log(">> XBMC is playing content...")
                        if (xbmc_player.isPlayingAudio() == 1):
                                info_tag = xbmc_player.getMusicInfoTag(object)
                                log(">> Music title: " + info_tag.getTitle())
                        if (xbmc_player.isPlayingVideo() == 1):
				xbmc_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
                                info_tag = xbmc_player.getVideoInfoTag(object)
                                log(">> Video title: " + info_tag.getTitle())
				log(">> Rating: " + str(info_tag.getRating()))
				log(">> Remaining time (minutes): " + str(round(xbmc_remaining_time/60)))
				# Pause Video
				if (settings.getSetting("xbmc_oncall_pause_media") == "true"):
					time.sleep(1)
					xbmc_new_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
					if(xbmc_remaining_time > xbmc_new_remaining_time):
						log(">> Pause media...")
       			                 	xbmc_player.pause()
						self.xbmc_player_paused = True
				# Redirect Incoming Call
				if (settings.getSetting("asterisk_now_playing_enabled") == "true"):
					log(">> Redirect call...")
					try:
						pbx.Setvar(event.Channel,"xbmc_remaining_time",round(xbmc_remaining_time/60))
						pbx.Redirect(event.Channel,settings.getSetting("asterisk_now_playing_context"))
					except:
						log(">> ERROR: %s::%s (%d) - %s" % (self.__class__.__name__,sys.exc_info()[2].tb_frame.f_code.co_name,sys.exc_info()[2].tb_lineno,sys.exc_info()[1],))
		# Show Incoming Call Notification Popup
		if (settings.getSetting("xbmc_oncall_notification") == "true"):
			arr_timeout = [5,10,15,20,25,30]
			xbmc_oncall_notification_timeout = int(arr_timeout[int(settings.getSetting("xbmc_oncall_notification_timeout"))])
			xbmc_notification = str_callerid
			log(">> Notification: " + xbmc_notification)
			xbmc.executebuiltin("XBMC.Notification("+ __language__(30050) +","+ xbmc_notification +","+ str(xbmc_oncall_notification_timeout*1000) +")")


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
		str_url = settings.getSetting("asterisk_info_url")
		str_url = str_url +"?vm&cdr&mailbox="+ settings.getSetting("asterisk_vm_mailbox")
		str_url = str_url +"&vmcontext="+ settings.getSetting("asterisk_vm_context")
		#log(">> " + str_url)
		f = urllib.urlopen(str_url)
		self.dom = xml.dom.minidom.parse(f)
		#log(self.dom.toxml())
		f.close()
		del f

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
			settings.openSettings()
			self.onInit()

	def onFocus(self,controlId):
		pass

	#####################################################################################################
	def make_outgoing_call(self,number_to_call):
		log("> make_outgoing_call()")
		manager_host_port = settings.getSetting("asterisk_manager_host"),int(settings.getSetting("asterisk_manager_port"))
		pbx = Manager(manager_host_port,settings.getSetting("asterisk_manager_user"),settings.getSetting("asterisk_manager_pass"))
        	pbx.Originate(settings.getSetting("asterisk_outbound_extension"),settings.getSetting("asterisk_outbound_context"),number_to_call,1)
		del pbx
		log(">> Done.")

	#####################################################################################################
	def play_voice_mail(self,recindex):
		log("> play_voice_mail()")
		audio_format = ["wav","gsm","mp3"]
		asterisk_vm_format = audio_format[int(settings.getSetting("asterisk_vm_format"))]
		url_vm = settings.getSetting("asterisk_info_url") +"?recindex="+ recindex
		url_vm = url_vm +"&mailbox="+ settings.getSetting("asterisk_vm_mailbox")
		url_vm = url_vm +"&vmcontext="+ settings.getSetting("asterisk_vm_context")
		url_vm = url_vm +"&format="+ asterisk_vm_format
		xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(url_vm)


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
		settings.openSettings()
		self.close()



#################################################################################################################
 # Starts here
#################################################################################################################

log("XBMC_HOME=%s" % XBMC_HOME)
settings = xbmc.Settings(path=os.getcwd())

RUNMODE_NORMAL = "NORMAL"
RUNMODE_SILENT = "SILENT"
try:
	run_mode = sys.argv[1].strip()
except:
	run_mode = RUNMODE_NORMAL
if (run_mode != RUNMODE_SILENT):
	try:
		log("Launching GUI...")
		first_time_use = settings.getSetting("first_time_use")
		settings.setSetting("first_time_use","false")
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
else:
	try:
		log("Running in background...")
		manager_host_port = settings.getSetting("asterisk_manager_host"),int(settings.getSetting("asterisk_manager_port"))
		pbx = Manager(manager_host_port,settings.getSetting("asterisk_manager_user"),settings.getSetting("asterisk_manager_pass"))
		vm = settings.getSetting("asterisk_vm_mailbox")+"@"+settings.getSetting("asterisk_vm_context")
		vm_count = tuple(pbx.MailboxCount(vm))
		xbmc_notification = __language__(30053) + str(vm_count[0])
		log(">> " + xbmc_notification)
		xbmc.executebuiltin("XBMC.Notification("+ __language__(30052) +","+ xbmc_notification +","+ str(15*1000) +")")
		grab = get_incoming_call()
		pbx.events += grab.events
		pbx.serve_forever()
	except:
		xbmc_notification = str(sys.exc_info()[1])
		log(">> " + xbmc_notification)
		xbmc.executebuiltin("XBMC.Notification("+ __language__(30051) +","+ xbmc_notification +","+ str(15*1000) +")")
	try:
		del grab
		del pbx
		sys.modules.clear()
	except:
		pass
try:
	del settings
except:
	pass

