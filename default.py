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

xbmc.output( __scriptname__ + " Version: " + __version__  + "\n" )
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString

import urllib, urlparse, urllib2
import re
import traceback
import xml.dom.minidom
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util

#############################################################################################################
def log(msg):
	try:
		xbmc.output("[%s]: %s\n" % (__scriptname__, msg))
	except:
		pass

# check if build is special:// aware - set roots paths accordingly
XBMC_HOME = 'special://home'
if not os.path.isdir(xbmc.translatePath(XBMC_HOME)):	# if fails to convert to Q:, old builds
	XBMC_HOME = 'Q:'
log("XBMC_HOME=%s" % XBMC_HOME)

#############################################################################################################
class get_incoming_call(object):
        '''
        Subscribe to Asterisk events, and get incoming calls.
        '''
        def __init__(self):
		log("__init__()")
                global xbmc_player
                xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		xbmc_player_paused = False
                self.ast_uniqid = 0
                self.events = Asterisk.Util.EventCollection()
                self.events.clear()
                self.events.subscribe('Newchannel', self.Newchannel)
                self.events.subscribe('NewCallerid', self.NewCallerid)
                self.events.subscribe('Hangup', self.Hangup)

	#####################################################################################################
        def Newchannel(self, pbx, event):
		#log("> NewChannel()")
                if event.ChannelStateDesc == 'Ring' and self.ast_uniqid == 0:
                        self.ast_uniqid = event.Uniqueid

	#####################################################################################################
        def NewCallerid(self, pbx, event):
		#log("> NewCallerid()")
                if event.Uniqueid == self.ast_uniqid and event.CallerIDName != "" and event.CallerIDNum != "":
                        self.newcall_actions(event)

	#####################################################################################################
        def Hangup(self, pbx, event):
		#log("> Hangup()")
                if event.Uniqueid == self.ast_uniqid:
                        self.ast_uniqid = 0
                        self.hangup_actions(event)

	#####################################################################################################
        def hangup_actions(self, event):
                log("> hangup_actions()")
                if xbmc_player.isPlaying() == 1:
			# Resume media
			if self.xbmc_player_paused:
                        	xbmc_player.pause()

	#####################################################################################################
        def newcall_actions(self, event):
		log("> newcall_actions()")
		self.xbmc_player_paused = False
                str_callerid = str(event.CallerIDName + "<"+ event.CallerIDNum +">")
                log(">> CallerID: " + str_callerid)
                settings = xbmc.Settings(path=os.getcwd())
                xbmc_oncall_notification = settings.getSetting("xbmc_oncall_notification")
		arr_timeout = [5,10,15,20,25,30]
                xbmc_oncall_notification_timeout = int(arr_timeout[int(settings.getSetting("xbmc_oncall_notification_timeout"))])
                xbmc_oncall_pause_media = settings.getSetting("xbmc_oncall_pause_media")
                del settings
                if xbmc_player.isPlaying() == 1:
                        log(">> XBMC is playing content...")
                        log("Remaining time: " + str(xbmc_player.getTotalTime() - xbmc_player.getTime()))
                        if xbmc_player.isPlayingAudio() == 1:
                                info_tag = xbmc_player.getMusicInfoTag(object)
                                log("Music title: " + info_tag.getTitle())
                        if xbmc_player.isPlayingVideo() == 1:
                                info_tag = xbmc_player.getVideoInfoTag(object)
                                log("Video title: " + info_tag.getTitle() + ", Rating: " + str(info_tag.getRating()))
			# Pause Media
			if (xbmc_oncall_pause_media == "true"):
				log("Pause media...")
                        	xbmc_player.pause()
				self.xbmc_player_paused = True
		# Show Incoming Call Notification Popup
		if (xbmc_oncall_notification == "true"):
			str_to_execute = "XBMC.Notification(" + __language__(30050) + ", " + str_callerid +", " + str(xbmc_oncall_notification_timeout * 1000) + ")"
			log(str_to_execute)
                	xbmc.executebuiltin(str_to_execute)


#############################################################################################################
class MainGUI(xbmcgui.WindowXML):
	# action codes
	ACTION_EXIT_SCRIPT = ( 9, 10 )

	def __init__( self, *args, **kwargs ):
		log("__init__()")
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )

	#####################################################################################################
        def onInit( self ):
		dialog = xbmcgui.DialogProgress()
		# Starting...
		dialog.create( __scriptname__, __language__(30061))
		# Reading Config...
		dialog.update(0, __language__(30062))
		self.getConfig()
		# Fetching Asterisk Info...
		dialog.update(25, __language__(30063))
		self.getInfo()
		# Displaying Asterisk Info...
		dialog.update(50, __language__(30064))
		self.showInfo("cdr")
		# Done...
		dialog.update(100, __language__(30065))
		dialog.close()
		del dialog
		log("Done.")

	#####################################################################################################
        def getConfig(self):
                log("> getConfig()")
		settings = xbmc.Settings(path=os.getcwd())
		self.asterisk_manager_host = settings.getSetting("asterisk_manager_host")
		self.asterisk_manager_port = int(settings.getSetting("asterisk_manager_port"))
		self.asterisk_manager_user = settings.getSetting("asterisk_manager_user")
		self.asterisk_manager_pass = settings.getSetting("asterisk_manager_pass")
		self.asterisk_outbound_extension = settings.getSetting("asterisk_outbound_extension")
		self.asterisk_outbound_context = settings.getSetting("asterisk_outbound_context")
		self.asterisk_info_url = settings.getSetting("asterisk_info_url")
		del settings

	#####################################################################################################
	def getInfo(self):
		log("> getInfo()")
		#log(self.asterisk_info_url)
		f = urllib.urlopen(self.asterisk_info_url + "?vm&cdr")
		self.dom = xml.dom.minidom.parse(f)
		#log(self.dom.toxml())
		f.close()
		del f

	#####################################################################################################
	def showInfo(self, option):
		log("> showInfo(" + option + ")")
		try:
			xbmcgui.lock()
			if ( option == "cdr" ):
				self.getControl(120).reset()
				self.getControl(120).setVisible(True)
				self.getControl(120).setEnabled(True)
				self.getControl(121).setVisible(False)
				self.getControl(121).setVisible(False)
			else:
				self.getControl(121).reset()
				self.getControl(121).setVisible(True)
				self.getControl(121).setEnabled(True)
				self.getControl(120).setVisible(False)
				self.getControl(120).setVisible(False)
			# Parse CDR/VM XML content
			for node in self.dom.getElementsByTagName(option):
				listitem = xbmcgui.ListItem()
				for childNode in node.childNodes:
					if (childNode.nodeName != "#text"):
						if ( childNode.firstChild ):
							listitem.setProperty( childNode.nodeName, childNode.firstChild.data )
						else:
							listitem.setProperty( childNode.nodeName, "" )
				if ( option == "cdr" ):
					self.getControl(120).addItem( listitem )
				else:
					self.getControl(121).addItem( listitem )
				del listitem
			xbmcgui.unlock()
		except:
			log("ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], ))

	#####################################################################################################
	def onAction(self, action):
		if ( action in self.ACTION_EXIT_SCRIPT ):
			self.close()

	def onClick( self, controlId ):
		log("> onClick(" + str(controlId) + ")")
		# Initiate outgoing call
		if ( controlId == 120 ):
			number_to_call = self.getControl(120).getSelectedItem().getProperty("src")
			if (number_to_call != ""):
				dialog = xbmcgui.Dialog()
				if (dialog.yesno(__scriptname__, __language__(30104) + " '" + number_to_call + "'?")):
					self.make_outgoing_call(number_to_call)
				del dialog
		# Play Voice Mail
		if ( controlId == 121 ):
			recindex = self.getControl(121).getSelectedItem().getProperty("recindex")
			if (recindex != ""):
				dialog = xbmcgui.Dialog()
				if (dialog.yesno(__scriptname__, __language__(30105))):
					xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(self.asterisk_info_url + "?recindex=" + recindex)
				del dialog
		# CDR/VM toggle
		elif ( controlId == 110 ):
			if ( self.getControl(110).getLabel() == __language__(30101) ):
				self.getControl(110).setLabel(__language__(30102))
				self.showInfo("vm")
			else:
				self.getControl(110).setLabel(__language__(30101))
				self.showInfo("cdr")
		# Settings
		elif ( controlId == 111 ):
			settings = xbmc.Settings(path=os.getcwd())
			settings.openSettings()
			del settings
			self.onInit()

	def onFocus(self, controlId ):
		pass

	#####################################################################################################
	def make_outgoing_call(self, number_to_call):
		log("> make_outgoing_call()")
        	pbx = Manager((self.asterisk_manager_host, self.asterisk_manager_port), self.asterisk_manager_user, self.asterisk_manager_pass)
        	pbx.Originate(self.asterisk_outbound_extension,self.asterisk_outbound_context,number_to_call,1)
		log("done.")


#################################################################################################################
 # Starts here
#################################################################################################################

RUNMODE_NORMAL = "NORMAL"
RUNMODE_SILENT = "SILENT"
try:
	run_mode = sys.argv[1].strip()
except:
	run_mode = RUNMODE_NORMAL
if ( run_mode != RUNMODE_SILENT ):
	# Launch GUI
	try:
		ui = MainGUI( "script_xbmc-pbx-addon_main.xml", os.getcwd(), "Default" )
		ui.doModal()
	except:
		log( str(sys.exc_info()[ 1 ]) )
	try:
		del ui
		self.dom.unlink()
		del self.dom
	except:
		pass
else:
	# Run in Background
	try:
                settings = xbmc.Settings(path=os.getcwd())
                asterisk_manager_host = settings.getSetting("asterisk_manager_host")
                asterisk_manager_port = int(settings.getSetting("asterisk_manager_port"))
                asterisk_manager_user = settings.getSetting("asterisk_manager_user")
                asterisk_manager_pass = settings.getSetting("asterisk_manager_pass")
                del settings
		pbx = Manager((asterisk_manager_host, asterisk_manager_port), asterisk_manager_user, asterisk_manager_pass)
		#
		# TODO: Handle errors connecting to the Asterisk Host
		#
		grab = get_incoming_call()
		pbx.events += grab.events
		pbx.serve_forever()
	except:
		log( str(sys.exc_info()[ 1 ]) )
	try:
		del grab
		del pbx
	except:
		pass

