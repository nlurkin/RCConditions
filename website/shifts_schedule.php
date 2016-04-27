<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("config.php");
include ("na62_helper.php");
include ("na62_shifts_lib.php");

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbShiftName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}
function buildTable($db, $from, $week) {
	$fromTS = strtotime ( $from ) + (7 * 24 * 60 * 60) * ($week - 1);
	if (date ( "H", $fromTS ) != 0)
		$fromTS = $fromTS + (24 - intval ( date ( "H", $fromTS ) )) * 60 * 60;
	$toTS = $fromTS + (6 * 24 * 60 * 60);
	
	$slots = getShiftsFromTo ( $db, $fromTS, $toTS );
	print "<h2>NA62 2016 run Shift Schedule Week " . $week . " - " . date ( "F d", $fromTS ) . " to " . date ( "F d", $toTS ) . "</h2><table style='width:1000px'><tr><th style='width:70px'>Week " . $week . "</th>";
	foreach ( $slots as $slot )
		print "<th>" . date ( "l - F d", $slot->date ) . "</th>";
	print "</tr><tr class='r1'><th rowspan='2'>Night Shift (00:00 to 8:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 0, 1 ) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 0, 2 ) . "</td>";
	
	print "</tr><tr class='r1'><th rowspan='2'>Day Shift (8:00 to 16:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 1, 1 ) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 1, 2 ) . "</td>";
	
	print "</tr><tr class='r1'><th rowspan='2'>Afternoon Shift (16:00 to 24:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 2, 1 ) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 2, 2 ) . "</td>";
	
	print "</tr></table>";
}
?>

<!DOCTYPE html>
<html>
<header>
	<title>NA62 Shifts Schedule</title>
	<link rel="stylesheet" type="text/css" href="na62.css">
	<link rel="stylesheet" type="text/css" href="collapse.css">
</header>
<body>
	<h1>Welcome to the NA62 shifts schedule website.</h1>

<?php
for($week = 1; $week <= 30; $week ++) {
	buildTable ( $db, "2016-04-25", $week );
}
?>
</body>
</html>