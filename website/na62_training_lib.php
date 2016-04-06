<?php
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

function getEntriesForSlots($db, $date){
	$booked = array();
	$db->executeGet("SELECT * FROM shifter_training WHERE Date BETWEEN '".date("Y-m-d", $date)." 00:00:00' AND '".date("Y-m-d", $date). " 23:59:59'");
	while($row = $db->next()){
		array_push($booked, $row);
	}
	return $booked;
}

function getNamesForSlots($db, $date){
	$booked = array();
	$entries = getEntriesForSlots($db, $date);
	foreach($entries as $row){
		array_push($booked, $row["Name"]." ".$row["Surname"]);
	}
	return $booked;
}

function getListSlots($db){
	$slots = array();
	$db->executeGet("SELECT * FROM shifter_sessions ORDER BY Date");
	while($row = $db->next()){
		array_push($slots, array("Date"=>strtotime($row["Date"]), "Message"=>$row["Message"]));
	}
	return $slots;
}


function findUserLike($db, $user){
	$user = str_replace("*", "%", $user);
	$results = array();
	$db->executeGet("SELECT * FROM shifter_training WHERE Name LIKE '" . $user . "' OR Surname LIKE '".$user."'");
	while($row = $db->next()){
		array_push($results, $row);
	}
	return $results;
}

function printOptionListSlots($db, $list, $selectedDate, $freeOnly){
	foreach($list as $slot){
		$availSlots = getAvailableSlots($db, $slot["Date"]);
		if($freeOnly && $availSlots<=0) continue;
		$selected = "";
		$message = "";
		echo $slot["Date"]." " . $selectedDate;
		if($slot["Date"]==$selectedDate) $selected = "selected='true'";
		if($slot["Message"]!="") $message = " - " . $slot["Message"];
		echo "<option value='".$slot["Date"]."' ".$selected.">".date("d/m/y", $slot["Date"])." - ".$availSlots." slots available".$message."</option>";
	}
}

function insertUser($db, $name, $surname, $email, $date){
	$db->executeGet("SELECT * FROM shifter_training WHERE Name LIKE '".$name."' AND Surname LIKE '". $surname."'");
	if($db->next()){
		echo "<script>alert('A training request with this name has already been recorded. Please write us at na62-shiftertraining@cern.ch')</script>";
	}
	else{
		if(!$db->executeUpdate("INSERT INTO shifter_training (Name, Surname, Email, Date, Attended) VALUES (?,?,?,?,?)", "ssssi", $name, $surname, 
				$email, date("Y-m-d", $date), 0)){
			die("Error! Unable to update database");
		}
		else{
			$text = "Dear ".$name." ".$surname.",\n\nYour booking for a shifter training session on the ".date("Y-m-d", $date).
					" has been recorded.\n\nWe remind you that the session starts at 14h on the day and is expected to finish around 17h30.".
					"The session takes place in the conference room in building 918.\n\nBest regards,\nThe Shift Training Crew.";
			mail($email, "Booking confirmation for shifter training session", $text,"From: na62-shiftertraining@cern.ch" );
			echo "<script>alert('Your request has been recorded and a confirmation e-mail\\nhas been sent to the address you provided.\\nThank you')</script>";
		}
	}
}

function updateUser($db, $userID, $name, $surname, $email, $date, $attended){
	if(!$db->executeUpdate("UPDATE shifter_training SET Name=?, Surname=?, Email=?, Date=?, Attended=? WHERE idshifter_training=?", "ssssii", $name, $surname,
			$email, date("Y-m-d", $date), $attended, $userID)){
		die("Error! Unable to update database");
	}
}

function deleteUser($db, $userID){
	if(!$db->executeUpdate("DELETE FROM shifter_training WHERE idshifter_training=?", "i", $userID)){
				die("Error! Unable to update database");
	}
	echo "User with ID " .$userID . " was deleted"; 
}

function sendMailToSession($db, $date, $subject, $body){
	$attendees = getEntriesForSlots($db, $date);
	$listEmails = array("na62-shiftertraining@cern.ch");
	foreach($attendees as $user){
		array_push($listEmails, $user["Email"]);
	}
	mail(implode($listEmails, ", "), $subject, $body, "From: na62-shiftertraining@cern.ch");
	echo "<script>alert('The email has been sent successfully')</script>";
}

?>