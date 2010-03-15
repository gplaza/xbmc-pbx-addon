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
		xbmc.executebuiltin("XBMC.Notification(Incoming Call, " + cid_cidname + "<"+ cid_cidnum +">, 5000)")

    def Hangup(self, pbx, event):
        '''
        Event handler for the Asterisk 'Hangup' event.
        '''
	hang_uniqid = event.Uniqueid
	if hang_uniqid == self.ast_uniqid:
		self.ast_uniqid = 0

    def __init__(self):
	self.ast_uniqid = 0
        self.events = Asterisk.Util.EventCollection()
	self.events.clear()
        self.events.subscribe('Newchannel', self.Newchannel)
        self.events.subscribe('NewCallerid', self.NewCallerid)
        self.events.subscribe('Hangup', self.Hangup)


# Connect to 'asterisk' hostname, using 'xbmc' username and 'xbmc' password.
pbx = Manager(('asterisk', 5038), 'xbmc', 'xbmc')
grab = get_incoming_call()
pbx.events += grab.events
pbx.serve_forever()

