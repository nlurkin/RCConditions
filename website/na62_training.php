<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("config.php");
include ("na62_helper.php");

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
	
	if(!$bad){
		$db->executeGet("SELECT * FROM shifter_training WHERE Name LIKE '".$_POST["name"]."' AND Surname LIKE '". $_POST["surname"]."'");
		if($db->next()){
			echo "<script>alert('A training request with this name has already been recorded. Please write us at na62-shiftertraining@cern.ch')</script>";
		}
		else{
			if(!$db->executeUpdate("INSERT INTO shifter_training (Name, Surname, Email, Date, Attended) VALUES (?,?,?,?,?)", "ssssi", $_POST["name"], $_POST["surname"], $_POST["email"], date("Y-m-d", $_POST["date"]), 0)){
				die("Error! Unable to update database");
			}
			else{
				echo "<script>alert('Your request has been recorded and a confirmation e-mail\\nhas been sent to the address you provided.\\nThank you')</script>";
				$text = "Dear ".$_POST["name"]." ".$_POST["surname"].",\n\nYour booking for a shifter training session on the ".date("Y-m-d", $_POST["date"])." has been recorded.\n\nWe remind you that the session starts at 14h on the day and is expected to finish around 17h30. The session takes place in the conference room in building 918.\n\nBest regards,\nThe Shift Training Crew.";
				mail($_POST["email"], "Booking confirmation for shifter training session", $text,"From: na62-shiftertraining@cern.ch" );
			}
		}
	}
}

function echoIfSet($varName){
	if(isset($_POST[$varName])){
		echo $_POST[$varName];
	}
}

function getAvailableSlots($db, $date){
	$booked = 0;
	$db->executeGet("SELECT COUNT(*) as tot FROM shifter_training WHERE Date BETWEEN '".date("Y-m-d", $date)." 00:00:00' AND '".date("Y-m-d", $date). " 23:59:59'");
	if($row = $db->next()){
		$booked = $row["tot"];
	}
	return 12-$booked;
}

function getNamesForSlotSlots($db, $date){
	$booked = array();
	$db->executeGet("SELECT Name,Surname FROM shifter_training WHERE Date BETWEEN '".date("Y-m-d", $date)." 00:00:00' AND '".date("Y-m-d", $date). " 23:59:59'");
	while($row = $db->next()){
		array_push($booked, $row["Name"]." ".$row["Surname"]);
	}
	return $booked;
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
$trainingTS = 0;

$trainingTS = mktime(0, 0, 0, 4, 8, 2016);
$availSlots = getAvailableSlots($db, $trainingTS);
$selected = "";
if(isset($_POST["date"]) && $trainingTS==$_POST["date"]) $selected = "selected";
if($availSlots>0)
	echo "<option value=".$trainingTS." ".$selected.">".date("d/m/y", $trainingTS)." - ".$availSlots." slots available</option>";

$i = 0;
$endTS = mktime(0, 0, 0, 11, 07, 2016);
$startDate = time();
if($startDate<mktime(0, 0, 0, 04, 19, 2016))
	$startDate = mktime(0, 0, 0, 04, 19, 2016);
while($trainingTS<$endTS){
	$trainingTS = strtotime("Tuesday + ".$i." week", $startDate);
	$availSlots = getAvailableSlots($db, $trainingTS);
	$selected = "";
	if(isset($_POST["date"]) && $trainingTS==$_POST["date"]) $selected = "selected";
	if($availSlots>0)
		echo "<option value=".$trainingTS." ".$selected.">".date("d/m/y", $trainingTS)." - ".$availSlots." slots available</option>";
	$i++;
}
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


<table border="1" style="width:600px">
<tr>
<th style="width:100px">Session date</th><th style="width:500px">Registered shifter</th>
<?php
$trainingTS = 0;
$i = 0;
$j = 0;
$css = Array (
		"r1",
		"r2"
		);

$trainingTS = mktime(0, 0, 0, 4, 8, 2016);
$availSlots = getNamesForSlotSlots($db, $trainingTS);
if(sizeof($availSlots)>0){
	echo "<tr class='".$css [$j % 2]."'><td>".date("Y-m-d", $trainingTS)."</td><td>".implode($availSlots, ", ")."</td></tr>";
	$j++;
}

$endTS = mktime(0, 0, 0, 11, 07, 2016);
$startDate = mktime(0, 0, 0, 04, 19, 2016);
while($trainingTS<$endTS){
	$trainingTS = strtotime("Tuesday + ".$i." week", $startDate);
	$availSlots = getNamesForSlotSlots($db, $trainingTS);
	if(sizeof($availSlots)>0){
		echo "<tr class='".$css [$j % 2]."'><td>".date("Y-m-d", $trainingTS)."</td><td>".implode($availSlots, ", ")."</td></tr>";
		$j++;
	}
	$i++;
}
?>
</table>
</body>
</html>
