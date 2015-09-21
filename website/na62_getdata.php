<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

include ("config.php");
include ("na62_helper.php");
include("na62_fetch.php");

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}

include("na62_getglobals.php");

if(isset( $_GET['from'] ) ) $from = $_GET['from'];
else $from=0;
if(isset( $_GET['max'] ) ) $max = $_GET['max'];
else $max = 10;

$dataArray = fetch_all($db, $from, $max);

if ($moreInfo) {
	$rowspan = 2;
	$colspan = 2;
	$commentSize = "500px";
} else {
	$rowspan = 1;
	$colspan = 1;
	$commentSize = "300px";
}

if (count ( $dataArray ) > 0) {
	$i = 0;
	$css = Array (
			"r1",
			"r2"
	);
	foreach ( $dataArray as $row ) {
		if (! isset ( $_GET ['view'] ) || $_GET ['view'] == "") {
			$triggerstring = prepare_trigger ( "search", $row );
			$enabledstring = prepare_enabled ( "all", $row );
		} else if ($_GET ['view'] == "search") {
			$enabledstring = prepare_enabled ( "search", $row );
			$triggerstring = prepare_trigger ( "search", $row );
		}
		echo "<tr class='d0 " . $css [$i % 2] . "' id='" . $row ['id'] . "'>";
		echo "<td>" . $row ['number'] . "</td><td>" . $row ['runtypename'] . "</td>";
		echo "<td>" . $row ['timestart'] . "</td><td>" . $row ['timestop'] . "</td>";
		if (! $moreInfo)
			echo "<td class='wrappable'>" . $enabledstring . "</td>";
		echo "<td style='text-align:right' class='wrappable' colspan=" . $colspan . ">" . $row ['startcomment'] . "</td>";
		echo "<td style='text-align:right' class='wrappable' rowspan=" . $rowspan . ">" . $triggerstring . "</td>";
		echo "<td rowspan=" . $rowspan . "><a href='na62_runlist.php?view=details&run_id=" . $row ['id'] . "'>Details</a></td>";

		$file_name = $row ['number'] . $_na62XmlExtension;
		$file_url = $_na62XmlAddress . $file_name;
		if (exists ( $file_url )) {
			echo "<td rowspan=" . $rowspan . "><a href='na62_runlist.php?view=downxml&run_id=" . $row ['id'] . "'>XML</a></td>";
		} else {
			echo "<td rowspan=" . $rowspan . "></td>";
		}
		echo "</tr>\n";
		if ($moreInfo) {
			echo "<tr class='d0 " . $css [$i % 2] . "'>";
			echo "<td colspan=1></td>";
			echo "<td>" . $row ["totalburst"] . "</td>";
			echo "<td>" . $row ["totalL0"] . "</td>";
			echo "<td class='wrappable'>" . $enabledstring . "</td>";
			echo "<td style='text-align:right' colspan=2>" . $row ["endcomment"] . "</td>";
			echo "</tr>\n";
		}
		$i ++;
	}
}

?>