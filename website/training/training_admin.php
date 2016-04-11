<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("../config.php");
include ("../na62_helper.php");
include ("../na62_training_lib.php");

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}


/// UPDATE_USER_VIEW
if (isset ( $_POST ["view"] ) && $_POST["view"]=="update_user") {
	for($i = 0; $i < $_POST ["nMatch"]; $i ++) {
		$id = $_POST ["id_" . $i];
		$name = $_POST ["name_" . $i];
		$surname = $_POST ["surname_" . $i];
		$email = $_POST ["email_" . $i];
		$date = $_POST ["date_" . $i];
		$attended = isset ( $_POST ["attended_" . $i] ) ? 1 : 0;
	
		if (isset ( $_POST ["delete_" . $i] )) {
			deleteUser ( $db, $id );
		} else {
			$bad = false;
			if (empty ( $name )) {
				echo "<div style='color:Red'>Please provide your name</div><br>";
				$bad = true;
			}
			if (empty ( $surname )) {
				echo "<div style='color:Red'>Please provide your surname</div><br>";
				$bad = true;
			}
			if ($date == 0) {
				echo "<div style='color:Red'>Please select a date</div><br>";
				$bad = true;
			}
			if (! filter_var ( $email, FILTER_VALIDATE_EMAIL )) {
				echo "<div style='color:Red'>This (" . $email . ") email address does not appear to be valid.</div><br>";
				$bad = true;
			}
			if (! $bad)
				updateUser ( $db, $id, $name, $surname, $email, $date, $attended );
		}
	}
}/// END UPDATE_USER_VIEW

/// UPDATE_ATTENDED_VIEW
if (isset ( $_POST ["view"] ) && $_POST["view"]=="update_attended") {
	for($i = 0; $i < $_POST ["nMatch"]; $i ++) {
		$id = $_POST ["userID_" . $i];
		$attended = isset ( $_POST ["attended_" . $i] ) ? 1 : 0;
		
		echo $id." ".$attended."<br>";
		updateAttended ( $db, $id, $attended );
	}
}/// END UPDATE_USER_VIEW

/// ADD_USER_VIEW
if (isset ( $_POST ["view"] ) && $_POST["view"]=="add_user") {
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
}/// END ADD_USER_VIEW


/// SEND_MAIL_VIEW
if (isset ( $_POST ["view"] ) && $_POST["view"]=="send_mail") {
	$bad = false;
	if(empty($_POST["subject"])){
		echo "<div style='color:Red'>Please provide a subject for the email</div><br>";
		$bad = true;
	}
	if(empty($_POST["body"])){
		echo "<div style='color:Red'>Please write the body of the message</div><br>";
		$bad = true;
	}

	if(!$bad)
		sendMailToSession($db, $_POST["session_search"], $_POST["subject"], $_POST["body"]);
}/// END SEND_MAIL_VIEW
?>
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>NA62 Shifter Training - Admin</title>
<link rel="stylesheet" type="text/css" href="../na62.css">
<link rel="stylesheet" type="text/css" href="../collapse.css">
</head>
<body>


	<div class="search-form">
	<h4>Search Shifter</h4>
		<form method="POST" action="training_admin.php">
			<input type="text" name="user_search"> <input type="hidden"
				name="view" value="user"> <input type="submit" name="submit"
				value="Search">
		</form>
	</div>
	<br>
	<br>
	<div class="search-form">
	<h4>Search Session</h4>
		<form method="POST" action="training_admin.php">
			<select name='session_search'>
			<?php printOptionListSlots ( $db, getListSlots ( $db ), null, false );?>
			</select>
			<input type="hidden" name="view" value="session">
			<input type="submit" name="submit" value="Search">
		</form>
	</div>
	<br>
	<br>
	<div class="search-form">
	<h4>Add Shifter</h4>
		<form method="POST" action="training_admin.php">
			<input type="hidden" name="view" value="add_user">
			Name : <input type='text' name='name'>
			Surname : <input type='text' name='surname'>
			Email : <input type='text' name='email'>
			Session date : <select name='date'>
			<?php printOptionListSlots ( $db, getListSlots ( $db ), null, true );?>
			</select>
			<input type="submit" name="submit" value="Add">
		</form>
	</div>
	<br>
	<br>
<?php
// / USER_SEARCH VIEW
if (isset ( $_POST ["view"] ) && ($_POST ["view"] == "user" | $_POST ["view"] == "update_user")) {
	?>
<form method="POST" action="training_admin.php">
		<input type="hidden" name="view" value="update_user">
		<table border="1">
			<tr>
				<th>Name</th>
				<th>Surname</th>
				<th>Email</th>
				<th>Date</th>
				<th>Attended</th>
				<th>Delete</th>
			</tr>
<?php
	$bad = false;
	if (! isset ( $_POST ["user_search"] )) {
		echo "User name is not set";
		$bad = true;
	}
	if (! $bad) {
		$userList = findUserLike ( $db, $_POST ["user_search"] );
		if (sizeof ( $userList ) > 0) {
			$slotsList = getListSlots ( $db );
			echo "<input type='hidden' name='user_search' value='" . $_POST ["user_search"] . "'>";
			echo "<input type='hidden' name='nMatch' value='" . sizeof ( $userList ) . "'>";
			$i = 0;
			$css = Array (
					"r1",
					"r2"
					);
			foreach ( $userList as $user ) {
				echo "<tr class='".$css [$i % 2]."'><td><input type='hidden' name='id_" . $i . "' value='" . $user ["idshifter_training"] . "'>";
				echo "<input type='text' name='name_" . $i . "' value='" . $user ["Name"] . "'></td>";
				echo "<td><input type='text' name='surname_" . $i . "' value='" . $user ["Surname"] . "'></td>";
				echo "<td><input type='text' name='email_" . $i . "' value='" . $user ["Email"] . "'></td>";
				echo "<td><select name='date_" . $i . "'>";
				printOptionListSlots ( $db, $slotsList, strtotime ( $user ["Date"] ), false );
				echo "</select></td>";
				echo "<td><input type='checkbox' name='attended_" . $i . "' value='1' " . ($user ["Attended"] == 1 ? "checked" : "") . "></td>";
				echo "<td><input type='checkbox' name='delete_" . $i . "' value='1'></td>";
				echo "</tr>";
				$i ++;
			}
		}
	}
	?>
</table>
<?php
	if (sizeof ( $userList ) > 0) {
		echo "<input type='submit' name='submit' value='Modify'>";
	}
	?>
</form>
<?php 
} /// END USER_SEARCH VIEW
?>



<?php
// / SESSION_SEARCH VIEW
if (isset ( $_POST ["view"] ) && ($_POST ["view"] == "session" || $_POST ["view"] == "send_mail" || $_POST["view"] == "update_attended")) {
	$date = $_POST["session_search"];
?>
<div class="leftarea">
<form method="POST" action="training_admin.php">
		<input type="hidden" name="view" value="update_attended">
		<input type="hidden" name="session_search" value="<?php echo $date;?>">
<table border="1" style="width:500px">
<tr><th colspan="2"><?php echo date("Y-m-d", $date); ?></th><th>Attended</th></tr>
<?php 
$attendees = getEntriesForSlots($db, $date);
$i=0;
$css = Array (
		"r1",
		"r2"
		);
foreach($attendees as $row){
	echo "<tr class='".$css [$i % 2]."'><td>".$row["Name"]." ".$row["Surname"]."</td><td>". 
		$row["Email"]."</td><td>".
		"<input type='hidden' name='userID_".$i."' value='".$row["idshifter_training"]."'>".
		"<input type='checkbox' name='attended_" . $i . "' value='1' " . ($row ["Attended"] == 1 ? "checked" : "") . "></td></tr>";
	$i++;
}
?>
<tr style='border:0px; border-style: none'><td colspan='2' style='border:0px; border-style: none'></td><td style='border:0px; border-style: none'><input type='submit' name='submit' value='Update'></td></tr>
</table>
<input type="hidden" name="nMatch" value="<?php echo sizeof($attendees);?>">
</form>
</div>
<div class="rightarea">
<div class="search-form">
<h4>Send email</h4>
<form method="post" action="training_admin.php">
<input type="hidden" name="view" value="send_mail">
<input type="hidden" name="session_search" value="<?php echo $date;?>">
<label for="subject">Subject:</label><input type="text" name="subject"><br>
<label for="body">Body:</label><textarea rows="15" cols="100" name="body"></textarea>
<br>
<input type="submit" name="submit" value="Send">
</form>
</div>
</div>
<?php 
} /// END SESSION_SEARCH VIEW
?>
</body>
</html>