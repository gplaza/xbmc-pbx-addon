<?php
/*
	XBMC PBX Addon
		Asterisk Historical Information

*/

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
$cdr_filename = "/var/log/asterisk/cdr-csv/Master.csv";
$cdr = array();
if (is_readable($cdr_filename)) {
	if (($handle = fopen($cdr_filename, "r")) !== FALSE) {
		while (($cdr_data = fgetcsv($handle, 4096, ",")) !== FALSE) {
			$cdr[] = $cdr_data;
		}
		fclose($handle);
	}
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

if (isset($_GET["vm"])) {
// VoiceMail
$vm_path  = '/var/spool/asterisk/voicemail/default/000/INBOX/';
if ($handle = opendir($vm_path)) {
    $vm = array();
    while (false !== ($file = readdir($handle))) {
        if ($file != "." && $file != ".." && strpos($file,".txt")) {
            $vm[$file] = parse_ini_file($vm_path . $file);
        }
    }
    closedir($handle);
}

// Convert VM Array into XML
foreach ($vm as $i => $c) {
	$node = $xmldoc->createElement("vm");
	$element = $xmldoc->createElement(file);
	$element->appendChild($xmldoc->createTextNode($i));
	$node->appendChild($element);
        foreach ($c as $key => $val) {
                $element = $xmldoc->createElement($key);
                $element->appendChild($xmldoc->createTextNode($val));
                $node->appendChild($element);
        }
        $xmlroot->appendChild($node);
}
unset($vm);
}

// Print XML
header ("content-type: text/xml");
echo $xmldoc->saveXML();
unset($xmldoc);
?>

