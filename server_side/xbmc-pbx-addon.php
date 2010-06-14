<?php
/*
	XBMC PBX Addon
		Asterisk Historical Information

*/

// Script constants
$__script__              = "XBMC PBX Addon";
$__scriptID__            = "script.xbmc-pbx-addon";
$__author__              = "hmronline";
$__url__                 = "http://code.google.com/p/xbmc-pbx-addon/";
$__svn_url__             = "http://xbmc-pbx-addon.googlecode.com/svn/trunk/xbmc-pbx-addon";
$__credits__             = "Team XBMC, py-Asterisk";
$__started__             = "04-03-2010";
$__date__                = "13-06-2010";
$__version__             = "0.0.5";

// YOU MAY WANT TO CUSTOMIZE THIS:
$cdr_filename = "/var/log/asterisk/cdr-csv/Master.csv";
$vm_path  = '/var/spool/asterisk/voicemail/';

// Make sure php-xml is installed in your system!
//#############################################################################################################
if (isset($_GET['recindex']) && isset($_GET['mailbox']) && isset($_GET['vmcontext']) && isset($_GET['format'])) {
	// VoiceMail Audio Download
	// Based on http://www.freepbx.org/trac/browser/freepbx/branches/2.7/amp_conf/htdocs/recordings/misc/audio.php
	$vm_path = $vm_path . $_GET['vmcontext'] . "/" . $_GET['mailbox'] . "/INBOX/";
	$path = $vm_path . "msg" . $_GET['recindex'] . "." . $_GET['format'];
	// See if the file exists
	if (!is_file($path)) { die("<b>404 File not found!</b>"); }
	// Gather relevent info about file
	$size = filesize($path);
	$name = basename($path);
	$extension = strtolower(substr(strrchr($name,"."),1));
	// This will set the Content-Type to the appropriate setting for the file
	$ctype ='';
	switch($extension) {
		case "mp3": $ctype="audio/mpeg"; break;
		case "wav": $ctype="audio/x-wav"; break;
		case "gsm": $ctype="audio/x-gsm"; break;
		// not downloadable
		default: die("<b>404 File not found!</b>"); break ;
	}
	// need to check if file is mislabeled or a liar.
	$fp=fopen($path, "rb");
	if ($size && $ctype && $fp) {
		header("Pragma: public");
		header("Expires: 0");
		header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
		header("Cache-Control: public");
		header("Content-Description: wav file");
		header("Content-Type: " . $ctype);
		header("Content-Disposition: attachment; filename=" . $name);
		header("Content-Transfer-Encoding: binary");
		header("Content-length: " . $size);
		fpassthru($fp);
	} 
}
else {
	header ("content-type: text/xml");
	$xmldoc = new DOMDocument();
	$xmldoc->formatOutput = true;
	$xmlroot = $xmldoc->createElement("pbx");
	$xmldoc->appendChild($xmlroot);
	if (isset($_GET["cdr"])) {
		// CDR
		$cdr_fields = array('accountcode','src','dst','dcontext',
		'clid','channel','dstchannel','lastapp','lastdata',
		'start','answer','end','duration','billsec',
		'disposition','amaflags','uniqueid','userfield');
		// Read CSV file and store into an Array
		$cdr = array();
		if (is_readable($cdr_filename)) {
			if (($handle = fopen($cdr_filename, "r")) !== FALSE) {
				while (($cdr_data = fgetcsv($handle, 4096, ",")) !== FALSE) {
					$cdr[] = $cdr_data;
				}
			fclose($handle);
			}
		}
		else {
			$node = $xmldoc->createElement("cdr_error");
			$element = $xmldoc->createElement("msg");
			$element->appendChild($xmldoc->createTextNode("Unable to read file: " . $cdr_filename));
			$node->appendChild($element);
			$xmlroot->appendChild($node);
		}
		// Filter, resize and reverse
		$cdr = array_slice($cdr,-50);
		$cdr = array_reverse($cdr);
		// Convert CDR Array into XML
		for ($i=0; $i < count($cdr); $i++) {
			$node = $xmldoc->createElement("cdr");
			for ($c=0; $c < count($cdr[$i]); $c++) {
				$element = $xmldoc->createElement($cdr_fields[$c]);
				$element->appendChild($xmldoc->createTextNode($cdr[$i][$c]));
				$node->appendChild($element);
			}
			$xmlroot->appendChild($node);
		}
		unset($cdr);
	}
	if (isset($_GET["vm"]) && isset($_GET['mailbox']) && isset($_GET['vmcontext'])) {
		// VoiceMail
		$vm_path = $vm_path . $_GET['vmcontext'] . "/" . $_GET['mailbox'] . "/INBOX/";
		if (is_readable($vm_path)) {
			if ($handle = opendir($vm_path)) {
				$vm = array();
				while (false !== ($file = readdir($handle))) {
					if ($file != "." && $file != ".." && strpos($file,".txt")) {
						$vm[str_replace(".txt","",str_replace("msg","",$file))] = parse_ini_file($vm_path . $file);
					}
				}
			closedir($handle);
			}
		}
		else {
			$node = $xmldoc->createElement("vm_error");
			$element = $xmldoc->createElement("msg");
			$element->appendChild($xmldoc->createTextNode("Unable to read directory: " . $vm_path));
			$node->appendChild($element);
			$xmlroot->appendChild($node);
		}
                // Filter, resize and reverse
                $vm = array_slice($vm,-50);
                $vm = array_reverse($vm);
		// Convert VM Array into XML
		if (count($vm) > 0) {
			foreach ($vm as $i => $c) {
				$node = $xmldoc->createElement("vm");
				$element = $xmldoc->createElement(recindex);
				$element->appendChild($xmldoc->createTextNode($i));
				$node->appendChild($element);
				foreach ($c as $key => $val) {
					$element = $xmldoc->createElement($key);
					$element->appendChild($xmldoc->createTextNode($val));
					$node->appendChild($element);
				}
				$xmlroot->appendChild($node);
			}
		}
		unset($vm);
	}
	// Print XML
	echo $xmldoc->saveXML();
	echo "<!-- ". $__script__ . $__version__ ." -->";
	unset($xmldoc);
}
?>

