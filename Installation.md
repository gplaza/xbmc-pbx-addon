


# Introduction #

This addon has two components:
  * A front-end, which runs on XBMC side as a _Program Add-on_;
  * A back-end, which runs on the PBX server side as part of the Asterisk itself and as PHP component;

# Download necessary files #

  1. Download latest version from here: http://code.google.com/p/xbmc-pbx-addon/downloads/list
    * Save this file somewhere, you will need it later;
    * We assume this file is named `script.xbmc-pbx-addon.zip`;

# PBX: Back-end Installation #

## Move files around ##
  1. Unzip the `script.xbmc-pbx-addon.zip` file you downloaded before;
  1. Find a directory named `backend_files` inside the file you just extracted;
  1. Using your favorite FTP program move this folder content to your PBX server;
    * You might try FileZilla if you don't have one: http://filezilla-project.org/

## PBX Time ##
  1. Log-in into your PBX server;
  1. Put the `manager_custom.conf` file into `/etc/asterisk/`;
  1. Edit this file, specially the IP address which has to be IP Address of your XBMC host;
    * Remove the trailing **;** in order to enable it;
  1. If you are not using a standard install of FreePBX and Asterisk make sure `/etc/asterisk/manager.conf` has an include line like this one:
```
#include manager_custom.conf
```
  1. Append the contents from `extensions_custom.conf.sample` to your own `/etc/asterisk/extensions_custom.conf`;
    * **DO NOT OVERWRITE IT**
  1. Put the `xbmc-pbx-addon.php` file somewhere you can access it from a web browser;
    * Probably you'll pace it here: `/var/www/html/`;
    * And you may reach it with the web browser at: `http://asterisk/xbmc-pbx-addon.php`;
    * Of course, you must already have a Web Server (i.e. Apache) running on the PBX server;
  1. Using a standard install of FreePBX and Asterisk you may not have to change any values in the PHP file;
    * Otherwise, do so;
  1. Once you've finished, restart your PBX software:
    * If you have FreePBX installed:
```
root-pbx$amportal restart
```
    * Otherwise:
```
root-pbx$/etc/init.d/asterisk restart
```

### Optional ###
  1. To stop Fail2Ban from banning XBMC while setting it up set:
```
ignoreip = [IP OF XBMC]
```
    * Do this in `/etc/fail2ban/jail.conf`;
  1. Also, restart it:
```
root-pbx$service fail2ban restart
```

# XBMC: Front-end Installation #

## Via zip file ##
  1. In XBMC, go to _System_ -> _Add-ons_ -> _Install from zip file_;
    * Find and select the `script.xbmc-pbx-addon.zip` file you downloaded before;
  1. You must see a notification pop-up saying **XBMC PBX Addon** is **Enabled**;

## Via Add-ons official repository ##
  1. In XBMC, go to _System_ -> _Add-ons_ -> _Get Add-ons_ -> _XBMC.org Add-ons_ -> _Program Add-ons_ -> _XBMC PBX Addon_;
  1. Select the **Install** option;
  1. You must see a notification pop-up saying **XBMC PBX Addon** is **Enabled**;

## Autoexec.py ##
  * For XBMC Eden, you don't need to worry about this;
  * For XBMC Dharma, copy the `autoexec.py` file (from the `script.xbmc-pbx-addon.zip` file you downloaded before) to `~/.xbmc/userdata/`;
  * For XBMC4XBOX 3.0.1, customize then copy the `autoexec.py` file (from the `script.xbmc-pbx-addon.zip` file you downloaded before) to `Q:\scripts`;

# XBMC: Front-end Configuration #
  1. In XBMC, go to _System_ -> _Add-ons_ -> _Enabled Add-ons_ -> _Program Add-ons_ -> _XBMC PBX Addon_ -> _Configure_;
  1. _Connection_:
    * Be very careful to put here the correct values for AMI (the ones you put in `/etc/asterisk/manager_custom.conf`);
    * Also set the **hostname** to the correct hostname or IP address for your PBX Server;
  1. _CDR & VoiceMail_:
    * Specify the URL you used with your web-browser to access the `xbmc-pbx-addon.php`;
    * Then you may want to change the **Mailbox number** for the one you would like to retrieve VoiceMail messages;
  1. _Outbound Calls_:
    * Customize it with the **extension** (and **context**) you would like to use when initiating outbound calls;
  1. _Inbound Calls_:
    * The first setting (**...NewChannel State**) defines how inbound calls are detected so you might try these values:
      * **Ring** if you have an _Asterisk 1.6_ PBX server;
      * **Down** if you have an _Asterisk 1.4_ PBX server;
    * Personalize the remaining settings to modify the XBMC and Asterisk behavior for inbound calls;
  1. _OK_:
    * Click **OK** for settings to be saved;

# XBMC Restart #
  1. Restart XBMC for the background service to automatically start;
  1. Once XBMC has loaded, you should see a notification pop-up showing the number of VoiceMail messages you have in your Mailbox;
    * If not, see the [Troubleshooting](Troubleshooting.md) page;

# XBMC: Front-end first run #
  1. To open (run) it, just go to _Programs_ from the XBMC home screen and find **XBMC PBX Addon**;
  1. In case you didn't if before, you will be prompted to configure this add-on;
  1. If everything went fine, you will see the front-end main screen with the list of your phone calls;
    * Otherwise see the [Troubleshooting](Troubleshooting.md) page;