'''
        XBMC PBX Addon
               Script (Running in Background)

'''

# Script constants
__script__              = "XBMC PBX Addon"
__scriptID__            = "script.xbmc-pbx-addon"
__author__              = "hmronline"
__url__                 = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__             = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__platform__            = "xbmc media center, [ALL]"
__credits__             = "Team XBMC, py-Asterisk"
__started__             = "04-03-2010"
__date__                = "05-07-2010"
__version__             = "0.0.6"
__svn_revision__        = "$Revision$".replace("Revision","").strip("$: ")
__XBMC_Revision__       = "20000"

xbmc.output(__script__ + " Version: " + __version__  + "\n")

# Modules
import sys, os
import xbmc
import re, traceback, time


CWD = os.getcwd().rstrip(";")
__language__ = xbmc.Language(CWD).getLocalizedString

sys.path.append(xbmc.translatePath(os.path.join(CWD,'resources','lib')))
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util



#############################################################################################################
def log(msg):
	try:
		xbmc.output("[%s]: %s\n" % (__script__,msg))
	except:
		pass

#############################################################################################################
class get_incoming_call(object):

        def __init__(self):
		log("__init__()")
		self.DEBUG = False
		global asterisk_series
		self.asterisk_series = asterisk_series
		if (self.DEBUG): log(">> Asterisk: " + self.asterisk_series)
		self.xbmc_player_paused = False
                self.ast_uniqid = 0
		self.event_callerid = ""
                self.events = Asterisk.Util.EventCollection()
                self.events.clear()
                self.events.subscribe('Newchannel',self.NewChannel)
                self.events.subscribe('Newcallerid',self.NewCallerID)		# Asterisk 1.4
                self.events.subscribe('NewCallerid',self.NewCallerID)		# Asterisk 1.6
                self.events.subscribe('Hangup',self.Hangup)

	#####################################################################################################
        def NewChannel(self,pbx,event):
		if (self.DEBUG):
			log("> NewChannel()")
			log(">> UniqueID: " + event.Uniqueid)
		if (self.asterisk_series == "1.4"):
			# Asterisk 1.4
			event_state = str(event.State)
		else:
			# Asterisk 1.6+
			event_state = str(event.ChannelStateDesc)
		if (self.DEBUG): log(">> State: " + event_state)
		arr_chan_states = ['Down','Ring']
		settings = xbmc.Settings(CWD)
		asterisk_chan_state = str(arr_chan_states[int(settings.getSetting("asterisk_chan_state"))])
		del settings
                if (event_state == asterisk_chan_state and self.ast_uniqid == 0):
                        self.ast_uniqid = event.Uniqueid
			if (self.DEBUG):
				log(">>> Uniqueid: " + self.ast_uniqid)
				log(">>> State: " + asterisk_chan_state)

	#####################################################################################################
        def NewCallerID(self,pbx,event):
		if (self.DEBUG):
			log("> NewCallerID()")
			log(">> UniqueID: " + event.Uniqueid)
		if (self.asterisk_series == "1.4"):
			# Asterisk 1.4
			event_callerid_num = str(event.CallerID)
		else:
			# Asterisk 1.6+
			event_callerid_num = str(event.CallerIDNum)
		if (event.CallerIDName != "" and event_callerid_num != ""):
			self.event_callerid = str(event.CallerIDName + " <" + event_callerid_num + ">")
		if (self.DEBUG): log(">> CallerID: " + self.event_callerid)
                if (event.Uniqueid == self.ast_uniqid and self.event_callerid != ""):
                        self.newcall_actions(event)

	#####################################################################################################
        def Hangup(self,pbx,event):
		if (self.DEBUG):
			log("> Hangup()")
			log(">> UniqueID: " + event.Uniqueid)
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
		if (self.DEBUG): log(">> UniqueID: " + self.ast_uniqid)
                log(">> CallerID: " + self.event_callerid)
		xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		settings = xbmc.Settings(CWD)
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
			xbmc_notification = self.event_callerid
			xbmc_img = xbmc.translatePath(os.path.join(CWD,'resources','images','xbmc-pbx-addon.png'))
			log(">> Notification: " + xbmc_notification)
			xbmc.executebuiltin("XBMC.Notification("+ __language__(30050) +","+ xbmc_notification +","+ str(xbmc_oncall_notification_timeout*1000) +","+ xbmc_img +")")
		del settings
		del xbmc_player


#################################################################################################################
 # Starts here
#################################################################################################################

try:
	log("Running in background...")
	settings = xbmc.Settings(CWD)
	manager_host_port = settings.getSetting("asterisk_manager_host"),int(settings.getSetting("asterisk_manager_port"))
	pbx = Manager(manager_host_port,settings.getSetting("asterisk_manager_user"),settings.getSetting("asterisk_manager_pass"))
	vm = settings.getSetting("asterisk_vm_mailbox") +"@"+ settings.getSetting("asterisk_vm_context")
	del settings
	asterisk_version = str(pbx.Command("core show version")[1])
	asterisk_series = asterisk_version[9:12]
	log(">> " + asterisk_version)
	vm_count = str(pbx.MailboxCount(vm)[0])
	xbmc_notification = __language__(30053) + vm_count
	xbmc_img = xbmc.translatePath(os.path.join(CWD,'resources','images','xbmc-pbx-addon.png'))
	log(">> Notification: " + xbmc_notification)
	xbmc.executebuiltin("XBMC.Notification("+ __language__(30052) +","+ xbmc_notification +","+ str(15*1000) +","+ xbmc_img +")")
	grab = get_incoming_call()
	pbx.events += grab.events
	pbx.serve_forever()
except:
	xbmc_notification = str(sys.exc_info()[1])
	xbmc_img = xbmc.translatePath(os.path.join(CWD,'resources','images','xbmc-pbx-addon.png'))
	log(">> Notification: " + xbmc_notification)
	xbmc.executebuiltin("XBMC.Notification("+ __language__(30051) +","+ xbmc_notification +","+ str(15*1000) +","+ xbmc_img +")")
try:
	del grab
	del pbx
	sys.modules.clear()
except:
	pass

