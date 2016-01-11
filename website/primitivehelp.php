<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );
// Get site specific configuration
include ("config.php");
include ("na62_helper.php");
include ("na62_fetch.php");
$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}

$detArray = fetch_PrimitiveMaskTypes ( $db );
?>
<html>
<head>
<title>NA62 run conditions Primitive help</title>
<link rel="stylesheet" type="text/css" href="na62.css">
</head>
<body>
	<h1>Details on the primitive triggers</h1>
	<a href="na62_runlist.php" class="back">Back</a>
	<div style="text-align: center; max-width: 600px; margin: 0 auto;">
		This page displays a list of all primitive triggers currently
		recorded. For each detector, the list of masks (in hexadecimal and
		binary form) are displayed along with their usual trigger name.</div>
	<div class="help_content">
		<div class="left_column">
			<h2>Detector A (CHOD)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [0] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
			<h2>Detector C (LAV)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [2] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
			<h2>Detector E (None)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [4] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
			<h2>Detector G (None)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [6] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
		</div>
		<div class="right_column">
			<h2>Detector B (RICH)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [1] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
			<h2>Detector D (MUV)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [3] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
			<h2>Detector F (TALK)</h2>
			<table border=1 style="table-layout: fixed; width: 450px">
				<tr>
					<th width="100px">Mask (hex)</th>
					<th width="250px">Mask (bin)</th>
					<th width="100px">Trigger</th>
				</tr>
		<?php
		$css = Array (
				"r1",
				"r2" 
		);
		foreach ( $detArray [5] as $key => $trigg ) {
			echo "<tr class='d0 " . $css [$key % 2] . "'>";
			echo "<td>" . implode ( "</td><td>", $trigg ) . "</td>";
			echo "</tr>";
		}
		?>
			</table>
		</div>
	</div>
</body>
</html>
