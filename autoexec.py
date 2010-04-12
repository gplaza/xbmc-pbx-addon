# Put this file into Q:\scripts folder to be executed when XBMC starts.
import os
import xbmc

# SILENT = Launch in background, to capture Asterisk events
# NORMAL = Launch GUI, interactive mode, to display CDR & VoiceMail
script_path = xbmc.translatePath(os.path.join(os.getcwd(),'My Scripts','xbmc-pbx-addon','default.py'))
print script_path
xbmc.executebuiltin("XBMC.RunScript(" + script_path + ", SILENT)")

