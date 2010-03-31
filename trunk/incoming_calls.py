'''
	XBMC PBX Addon
		Incoming calls handler
    
'''

__scriptname__ = "XBMC PBX Addon"
__author__ = "hmronline"
__url__ = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__ = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__credits__ = "XBMC Team, py-Asterisk"
__version__ = "0.0.1"


import xbmc, xbmcgui
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util

class get_incoming_call(object):
	'''
	Subscribe to Asterisk events, and get incoming calls.
	'''

	def Newchannel(self, pbx, event):
	        '''
		Event handler for the Asterisk 'Newchannel' event.
		'''
		ch_uniqid = event.Uniqueid
		ch_status = event.ChannelStateDesc
		if ch_status == 'Ring' and self.ast_uniqid == 0:
			self.ast_uniqid = ch_uniqid

	def NewCallerid(self, pbx, event):
		'''
		Event handler for the Asterisk 'NewCallerid' event.
		'''
		cid_cidname = event.CallerIDName
		cid_cidnum = event.CallerIDNum
		cid_uniqid = event.Uniqueid
		if cid_uniqid == self.ast_uniqid and cid_cidname != "" and cid_cidnum != "":
			print "CallerID: %s <%s>" % (cid_cidname, cid_cidnum)
			self.newcall_actions(event)

	def Hangup(self, pbx, event):
		'''
		Event handler for the Asterisk 'Hangup' event.
		'''
		hang_uniqid = event.Uniqueid
		if hang_uniqid == self.ast_uniqid:
			self.ast_uniqid = 0
			self.hangup_actions(event)


	def hangup_actions(self, event):
		'''
		Defines what to do during hangup call events
		'''
		if xbmc_player.isPlaying() == 1:
			xbmc_player.pause()

	def newcall_actions(self, event):
		'''
		Defines what to do during new call events
		'''
		if xbmc_player.isPlaying() == 1:
			print "Remaining time: %s" % (xbmc_player.getTotalTime() - xbmc_player.getTime())
			xbmc_player.pause()
			if xbmc_player.isPlayingAudio() == 1:
				info_tag = xbmc.InfoTagMusic(object)
				print "Music title: %s" % (info_tag.getTitle())
			if xbmc_player.isPlayingVideo() == 1:
				#info_tag = xbmc.InfoTagVideo(object)
				#print "Video title: %s, Rating: %s" % (info_tag.getTitle(), info_tag.getRating())
				pass
		xbmc.executebuiltin("XBMC.Notification(Incoming Call, " + event.CallerIDName + "<"+ event.CallerIDNum +">, 5000)")

	def __init__(self):
		global xbmc_player
		xbmc_player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		self.ast_uniqid = 0
		self.events = Asterisk.Util.EventCollection()
		self.events.clear()
		self.events.subscribe('Newchannel', self.Newchannel)
		self.events.subscribe('NewCallerid', self.NewCallerid)
		self.events.subscribe('Hangup', self.Hangup)



if ( __name__ == "__main__" ):
	# Connect to 'asterisk' hostname, using 'xbmc' username and 'xbmc' password.
	pbx = Manager(('asterisk', 5038), 'xbmc', 'xbmc')
	grab = get_incoming_call()
	pbx.events += grab.events
	pbx.serve_forever()
	del grab
	del pbx

