'''
        XBMC PBX Addon
               Script (Running in Background)

'''

import sys, os, os.path
import xbmc

# Script constants
__scriptname__ = "XBMC PBX Addon"
__author__ = "hmronline"
__url__ = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__ = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__credits__ = "XBMC Team, py-Asterisk"
__version__ = "0.0.5"

xbmc.output(__scriptname__ + " Version: " + __version__  + "\n")
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(os.getcwd(),'resources','lib'))
sys.path.append(BASE_RESOURCE_PATH)

import re, traceback, time
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util

__language__ = xbmc.Language(os.getcwd()).getLocalizedString

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
		arr_chan_states = ['Down','Ring']
		settings = xbmc.Settings(path=os.getcwd())
		asterisk_chan_state = str(arr_chan_states[int(settings.getSetting("asterisk_chan_state"))])
		del settings
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
		xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
                if (xbmc_player.isPlaying() == 1):
			# Resume media
			xbmc_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
			time.sleep(1)
			xbmc_new_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
			if (self.xbmc_player_paused and xbmc_remaining_time == xbmc_new_remaining_time):
				log(">> Resume media...")
                        	xbmc_player.pause()
				self.xbmc_player_paused = False
		del xbmc_player

	#####################################################################################################
        def newcall_actions(self,event):
		log("> newcall_actions()")
		log(">> Channel: " + str(event.Channel))
		#log(">> Unique ID: " + self.ast_uniqid)
                str_callerid = str(event.CallerIDName + " <"+ event.CallerIDNum +">")
                log(">> CallerID: " + str_callerid)
		xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		settings = xbmc.Settings(path=os.getcwd())
                if (xbmc_player.isPlaying() == 1):
                        log(">> XBMC is playing content...")
                        if (xbmc_player.isPlayingAudio() == 1):
                                info_tag = xbmc_player.getMusicInfoTag(object)
                                log(">> Music title: " + info_tag.getTitle())
				del info_tag
                        if (xbmc_player.isPlayingVideo() == 1):
				xbmc_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
                                info_tag = xbmc_player.getVideoInfoTag(object)
				xbmc_video_title = info_tag.getTitle()
				xbmc_video_rating = info_tag.getRating()
				del info_tag
                                log(">> Video title: " + xbmc_video_title)
				log(">> Rating: " + str(xbmc_video_rating))
				log(">> Remaining time (minutes): " + str(round(xbmc_remaining_time/60)))
				# Pause Video
				if (settings.getSetting("xbmc_oncall_pause_media") == "true"):
					time.sleep(1)
					xbmc_new_remaining_time = xbmc_player.getTotalTime() - xbmc_player.getTime()
					if (xbmc_remaining_time > xbmc_new_remaining_time):
						log(">> Pause media...")
       			                 	xbmc_player.pause()
						self.xbmc_player_paused = True
				# Redirect Incoming Call
				if (settings.getSetting("asterisk_now_playing_enabled") == "true"):
					log(">> Redirect call...")
					try:
						asterisk_alert_info = str(pbx.Getvar(event.Channel,"ALERT_INFO",""))
						log(">> ALERT_INFO: " + asterisk_alert_info)
						if (asterisk_alert_info == settings.getSetting("asterisk_alert_info")):
							pbx.Setvar(event.Channel,"xbmc_video_title",xbmc_video_title)
							pbx.Setvar(event.Channel,"xbmc_remaining_time",round(xbmc_remaining_time/60))
							pbx.Redirect(event.Channel,settings.getSetting("asterisk_now_playing_context"))
					except:
						log(">> ERROR: %s::%s (%d) - %s" % (self.__class__.__name__,sys.exc_info()[2].tb_frame.f_code.co_name,sys.exc_info()[2].tb_lineno,sys.exc_info()[1],))
		# Show Incoming Call Notification Popup
		if (settings.getSetting("xbmc_oncall_notification") == "true"):
			arr_timeout = [5,10,15,20,25,30]
			xbmc_oncall_notification_timeout = int(arr_timeout[int(settings.getSetting("xbmc_oncall_notification_timeout"))])
			xbmc_notification = str_callerid
			xbmc_img = xbmc.translatePath(os.path.join(os.getcwd(),'resources','images','xbmc-pbx-addon.png'))
			log(">> Notification: " + xbmc_notification)
			xbmc.executebuiltin("XBMC.Notification("+ __language__(30050) +","+ xbmc_notification +","+ str(xbmc_oncall_notification_timeout*1000) +","+ xbmc_img +")")
		del settings
		del xbmc_player


#################################################################################################################
 # Starts here
#################################################################################################################

log("XBMC_HOME=%s" % XBMC_HOME)

try:
	log("Running in background...")
	settings = xbmc.Settings(path=os.getcwd())
	manager_host_port = settings.getSetting("asterisk_manager_host"),int(settings.getSetting("asterisk_manager_port"))
	pbx = Manager(manager_host_port,settings.getSetting("asterisk_manager_user"),settings.getSetting("asterisk_manager_pass"))
	vm = settings.getSetting("asterisk_vm_mailbox") +"@"+ settings.getSetting("asterisk_vm_context")
	del settings
	vm_count = tuple(pbx.MailboxCount(vm))
	xbmc_notification = __language__(30053) + str(vm_count[0])
	xbmc_img = xbmc.translatePath(os.path.join(os.getcwd(),'resources','images','xbmc-pbx-addon.png'))
	log(">> " + xbmc_notification)
	xbmc.executebuiltin("XBMC.Notification("+ __language__(30052) +","+ xbmc_notification +","+ str(15*1000) +","+ xbmc_img +")")
	grab = get_incoming_call()
	pbx.events += grab.events
	pbx.serve_forever()
except:
	xbmc_notification = str(sys.exc_info()[1])
	xbmc_img = xbmc.translatePath(os.path.join(os.getcwd(),'resources','images','xbmc-pbx-addon.png'))
	log(">> " + xbmc_notification)
	xbmc.executebuiltin("XBMC.Notification("+ __language__(30051) +","+ xbmc_notification +","+ str(15*1000) +","+ xbmc_img +")")
try:
	del grab
	del pbx
	sys.modules.clear()
except:
	pass

