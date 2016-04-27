<?php
function echoIfSet($varName){
	if(isset($_POST[$varName])){
		echo $_POST[$varName];
	}
}

function getSessionID($db, $date){
	$db->executeGet("SELECT session_id FROM shifters.training_sessions WHERE date='".date("Y-m-d", $date) . "'");
	if($row = $db->next()){
		return $row["session_id"];
	}
	return -1;
}

function getUserID($db, $name, $surname){
	$db->executeGet("SELECT * FROM shifters.shifter WHERE name like '" . $name . "' and surname like '" . $surname . "'");
	if($row = $db->next()){
		return $row["id"];
	}
	return -1;
}

function getAvailableSlots($db, $date){
	$booked = 0;
	$session_id = getSessionID($db, $date);
	if($session_id==-1)
		return -99;
	$db->executeGet("SELECT COUNT(*) as tot FROM shifters.training_booking WHERE session_id=" . $session_id);
	if($row = $db->next()){
		$booked = $row["tot"];
	}
	return 12-$booked;
}

function getEntriesForSlots($db, $date){
	$booked = array();
	$session_id = getSessionID($db, $date);
	if($session_id==-1)
		return $booked;
	$db->executeGet("SELECT * FROM shifters.shifter_booking WHERE session_id=" . $session_id);
	while($row = $db->next()){
		array_push($booked, $row);
	}
	return $booked;
}

function getNamesForSlots($db, $date){
	$booked = array();
	$entries = getEntriesForSlots($db, $date);
	foreach($entries as $row){
		array_push($booked, $row["name"]." ".$row["surname"]);
	}
	return $booked;
}

function getListSlots($db){
	$slots = array();
	$db->executeGet("SELECT * FROM shifters.training_sessions ORDER BY Date");
	while($row = $db->next()){
		array_push($slots, array("date"=>strtotime($row["date"]), "message"=>$row["message"]));
	}
	return $slots;
}


function findUserLike($db, $user){
	$user = str_replace("*", "%", $user);
	$results = array();
	$db->executeGet("SELECT * FROM shifters.shifter_booking WHERE Name LIKE '" . $user . "' OR Surname LIKE '".$user."'");
	while($row = $db->next()){
		array_push($results, $row);
	}
	return $results;
}

function printOptionListSlots($db, $list, $selectedDate, $freeOnly){
	foreach($list as $slot){
		$availSlots = getAvailableSlots($db, $slot["date"]);
		if($freeOnly && $availSlots<=0) continue;
		$selected = "";
		$message = "";
		echo $slot["date"]." " . $selectedDate;
		if($slot["date"]==$selectedDate) $selected = "selected='true'";
		if($slot["message"]!="") $message = " - " . $slot["message"];
		echo "<option value='".$slot["date"]."' ".$selected.">".date("d/m/y", $slot["date"])." - ".$availSlots." slots available".$message."</option>";
	}
}

function insertShifter($db, $name, $surname, $email){
	$shifterID = getUserID($db, $name, $surname);
	$email_cern = NULL;
	$email_priv = NULL;
	if(strpos($email, "@cern.ch")!=False)
		$email_cern = $email;
	else
		$email_priv = $email;
	if($shifterID!=-1){
		$db->executeUpdate("UPDATE shifters.shifter SET email_cern=?, email_priv=? WHERE id=?", "ssi", $email_cern, $email_priv, $shifterID);
	}
	else 
		$db->executeUpdate("INSERT INTO shifters.shifter (name, surname, email_cern, email_priv) VALUES (?,?,?,?)", "ssss", $name, $surname, $email_cern, $email_priv);
}

function createBooking($db, $shifterID, $date, $name, $surname, $email){
	if(insertUserBooking($db, $shifterID, $date)){
		$text = "Dear ".$name." ".$surname.",\n\nYour booking for a shifter training session on the ".date("Y-m-d", $date).
		" has been recorded.\n\nWe remind you that the session starts at 14h on the day and is expected to finish around 17h30.".
		"The session takes place in the conference room in building 918.\n\nBest regards,\nThe Shift Training Crew.";
		mail($email, "Booking confirmation for shifter training session", $text,"From: na62-shiftertraining@cern.ch" );
		echo "<script>alert('Your request has been recorded and a confirmation e-mail\\nhas been sent to the address you provided.\\nThank you')</script>";
	}	
}

function insertUserBooking($db, $shifterID, $date){
	$db->executeGet("SELECT * FROM shifters.training_booking WHERE shifter_id=" . $shifterID);
	if($db->next()){
		echo "<script>alert('A training request with this name has already been recorded. Please write us at na62-shiftertraining@cern.ch')</script>";
		return;
	}
	
	$sessionID = getSessionID($db, $date);
	if($sessionID==-1){
		echo "<script>alert('You are trying to book for a session that does not exist.')</script>";
		return;
	}
	if(!$db->executeUpdate("INSERT INTO shifters.training_booking (shifter_id, session_id, attended) VALUES (?,?,?)", "iii", $shifterID, $sessionID, 0)){
		die("Error! Unable to update database");
	}
	return true;
}

function updateShifter($db, $shifterID, $name, $surname, $email){
	$email_cern = NULL;
	$email_priv = NULL;
	if(strpos($email, "@cern.ch")!=False)
		$email_cern = $email;
	else
		$email_priv = $email;
	
	if(!$db->executeUpdate("UPDATE shifters.shifter SET name=?, surname=?, email_cern=?, email_priv=? WHERE id=?", "ssssi", $name, $surname,
			$email_cern, $email_priv, $shifterID)){
		die("Error! Unable to update database");
	}
}

function updateBooking($db, $bookingID, $date, $attended){
	$sessionID = getSessionID($db, $date);
	if(!$db->executeUpdate("UPDATE shifters.training_booking SET session_id=?, attended=? WHERE id=?", "iii", $sessionID, $attended, $bookingID)){
				die("Error! Unable to update database");
	}
}

function updateAttended($db, $bookingID, $attended){
	if(!$db->executeUpdate("UPDATE shifters.training_booking SET attended=? WHERE id=?", "ii", $attended, $bookingID)){
		die("Error! Unable to update database");
	}
}

function deleteBooking($db, $bookingID){
	if(!$db->executeUpdate("DELETE FROM shifters.training_booking WHERE id=?", "i", $bookingID)){
				die("Error! Unable to update database");
	}
	echo "Booking with ID " .$bookingID . " was deleted"; 
}

function sendMailToSession($db, $date, $subject, $body){
	$attendees = getEntriesForSlots($db, $date);
	$listEmails = array("na62-shiftertraining@cern.ch");
	foreach($attendees as $user){
		if($user["email_cern"]!==NULL)
			array_push($listEmails, $user["email_cern"]);
		if($user["email_priv"]!==NULL)
			array_push($listEmails, $user["email_priv"]);
	}
	mail(implode($listEmails, ", "), $subject, $body, "From: na62-shiftertraining@cern.ch");
	echo "<script>alert('The email has been sent successfully')</script>";
}

?>