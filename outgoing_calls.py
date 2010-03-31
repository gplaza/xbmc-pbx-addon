'''
        XBMC PBX Addon
                Outgoing calls handler

'''

__scriptname__ = "XBMC PBX Addon"
__author__ = "hmronline"
__url__ = "http://code.google.com/p/xbmc-pbx-addon/"
__svn_url__ = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon"
__credits__ = "XBMC Team, py-Asterisk"
__version__ = "0.0.1"



#import xbmc, xbmcgui
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util


if ( __name__ == "__main__" ):
        # Connect to 'asterisk' hostname, using 'xbmc' username and 'xbmc' password.
        pbx = Manager(('asterisk', 5038), 'xbmc', 'xbmc')
	num_to_call = '666'
	using_context = 'from-internal'
	ext_making_call = 'Local/200@from-internal'
	
	pbx.Originate(ext_making_call,using_context,num_to_call,1)

