
#import xbmc, xbmcgui
from Asterisk.Manager import Manager
import Asterisk.Manager, Asterisk.Util


# Connect to 'asterisk' hostname, using 'xbmc' username and 'xbmc' password.
pbx = Manager(('asterisk', 5038), 'xbmc', 'xbmc')

num_to_call = '666'
using_context = 'from-internal'
ext_making_call = 'Local/200@from-internal'

pbx.Originate(ext_making_call,using_context,num_to_call,1)

