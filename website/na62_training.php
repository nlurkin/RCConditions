<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("config.php");
include ("na62_helper.php");
include ("na62_training_lib.php");

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}

if(isset($_POST["submit"])){
	$bad = false;
	if(empty($_POST["name"])){
		echo "<div style='color:Red'>Please provide your name</div><br>";
		$bad = true;
	}
	if(empty($_POST["surname"])){
		echo "<div style='color:Red'>Please provide your surname</div><br>";
		$bad = true;
	}
	if($_POST["date"]==0){
		echo "<div style='color:Red'>Please select a date</div><br>";
		$bad = true;
	}
	if (!filter_var($_POST["email"], FILTER_VALIDATE_EMAIL)) {
		echo "<div style='color:Red'>This (".$_POST["email"].") email address does not appear to be valid.</div><br>";
		$bad = true;
	}
	
	if(!$bad)
		insertUser($db, $_POST["name"], $_POST["surname"], $_POST["email"], $_POST["date"]);
}
?>
<!DOCTYPE html>
<html>
<header>
<title>NA62 Shifter Training</title>
<link rel="stylesheet" type="text/css" href="na62.css">
<link rel="stylesheet" type="text/css" href="collapse.css">
</header>
<body>
<h1>Welcome to the NA62 shifter training website.</h1>
<br>
To book a training session, please enter your name and select one of the available training dates.<br>
The training sessions are organised during the run every Tuesday starting at 14h and ending approximately at 17h30.<br><br>
<div class="search-form">
<form action="na62_training.php" method="POST">
<table>
<tr>
<td style="width:200px">Name: </td><td><input type="text" name="name" value="<?php echoIfSet("name"); ?>"></input></td>
</tr>
<tr>
<td>Surname:</td><td><input type="text" name="surname" value="<?php echoIfSet("surname"); ?>"></input></td>
</tr>	
<tr>
<td>Email address (for confirmation):</td><td><input type="text" name="email" value="<?php echoIfSet("email"); ?>"></input></td>
</tr>	
<tr>
<td>Training date:</td><td><select name="date">
<option value=0> Please select a date</option>
<?php
$listSlots = getListSlots($db);
$date = null;
if(isset($_POST["date"])) $date = $_POST["date"];
printOptionListSlots($db, $listSlots, $date, true);
?>
</select></td>
</tr>
<tr>
<td></td><td>
<input type="submit" name="submit" value="Submit"></td>
</table>
</form>
</div>
<br>
If you have any special request or need to book a slot for a sessions that appears to be fully booked, please contact us at 
<a href="mailto:na62-shiftertraining@cern.ch">na62-shiftertraining@cern.ch</a><br>

<br>
<br>


<table border="1" style="width:800px">
<tr>
<th style="width:100px">Session date</th><th style="width:300px">Comment</th><th style="width:500px">Registered shifter</th>
<?php

$i = 0;
$j = 0;
$css = Array (
		"r1",
		"r2"
		);

$listSlots = getListSlots($db);

foreach($listSlots as $slot){
	$availSlots = getNamesForSlots($db, $slot["Date"]);
	if(sizeof($availSlots)>0){
		echo "<tr class='".$css [$j % 2]."'><td>".date("Y-m-d", $slot["Date"])."</td><td>".$slot["Message"]."</td><td>".implode($availSlots, ", ")."</td></tr>";
		$j++;
	}
}
?>
</table>
</body>
</html>
