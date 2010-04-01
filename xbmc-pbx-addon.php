<?php
/*
	XBMC PBX Addon
		Asterisk Historical Information

*/

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

// Convert Array into XML
$xmldoc = new DOMDocument();
$xmldoc->formatOutput = true;
$xmlroot = $xmldoc->createElement("pbx");
$xmldoc->appendChild($xmlroot);
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


// Print XML
echo $xmldoc->saveXML();
?>

