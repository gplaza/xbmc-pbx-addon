# Put this file into the scripts folder to be executed when XBMC starts.
# That is Q:\scripts on XBMC4Xbox
# Or /home/<username>/.xbmc/scripts on Linux XBMC pre-Dharma versions.
# Or /home/<username>/.xbmc/userdata on Linux XBMC Dharma versions

import os
import xbmc

# Change this path according your XBMC setup (you may not need the '..' and 'addons')
script_path = xbmc.translatePath(os.path.join(os.getcwd(),'..','addons','script.xbmc-pbx-addon','bgservice.py'))
xbmc.executescript(script_path)

# This file should be deprecated for XBMC Eden release.
