<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("../config.php");
include ("../na62_helper.php");
include ("../na62_shifts_lib.php");
include ("../na62_training_lib.php");

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbShiftName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}
?>

<html>
<header>
	<title>NA62 Shifts Administration</title>
	<link rel="stylesheet" type="text/css" href="../na62.css">
	<link rel="stylesheet" type="text/css" href="../collapse.css">

	<script type="text/javascript">
function modifyID(id, institute, shifter, canceled, date, slot, type, week){
	if(id.length==0){
		document.getElementById("slot_id1").value = "";
		document.getElementById("shifter_name1").placeholder = "Please enter shifter surname";
		document.getElementById("shifter_name1").value = "";
		document.getElementById("institute1").placeholder = "Please enter shifter institute";
		document.getElementById("institute1").value = "";
		document.getElementById("delete").style.display = "none";
	}
	if(id.length>=1){
		document.getElementById("slot_id1").value = id[0];
		document.getElementById("shifter_name1").value = shifter[0];
		document.getElementById("institute1").value = institute[0];
		document.getElementById("delete").style.display = "inline";
	}
	if(id.length>1){
		document.getElementById("slot_id2").value = id[1];
		document.getElementById("shifter_name2").value = shifter[1];
		document.getElementById("institute2").value = institute[1];
	}
	else{
		document.getElementById("slot_id2").value = "";
		document.getElementById("shifter_name2").value = "";
		document.getElementById("institute2").value = "";
	}

	document.getElementById("canceled").checked = canceled;
	document.getElementById("date").value = date;
	document.getElementById("slot").value = slot;
	document.getElementById("type").value = type;
	
	document.getElementById("mod_div").style.display = "block";

	document.getElementById("formModify").action = "shifts_admin.php#week" + week;
}

function hideModify(){
	document.getElementById("mod_div").style.display = "none";
}
</script>
</header>
<body>

<?php 
function buildTable($db, $from, $week) {
	$fromTS = strtotime ( $from ) + (7 * 24 * 60 * 60) * ($week - 1);
	if (date ( "H", $fromTS ) != 0)
		$fromTS = $fromTS + (24 - intval ( date ( "H", $fromTS ) )) * 60 * 60;
	$toTS = $fromTS + (6 * 24 * 60 * 60);
	
	$slots = getShiftsFromTo ( $db, $fromTS, $toTS );
	print "<a name='week" . $week . "'></a>";
	print "<h2>NA62 2016 run Shift Schedule Week " . $week . " - " . date ( "F d", $fromTS ) . 
		" to " . date ( "F d", $toTS ) . "</h2>";
	print "<form action='shifts_admin.php#week".$week."' method='POST'>";
	print "<input type='text' name='week_comment' value='" . getWeekComment($db, $week, false) . "' style='width:800px'>";
	print "<input type='hidden' name='week_num' value='" . $week . "'> ";
	print "<input type='hidden' name='view' value='mod_comment'> ";
	print "<input type='submit' name='submit' value='Modify'>";
	print "</form>";
	print "<table style='width:1000px'><tr><th style='width:70px'>Week " . $week . "</th>";
	foreach ( $slots as $slot )
		print "<th>" . date ( "l - F d", $slot->date ) . "</th>";
	print "</tr><tr class='r1'><th rowspan='2'>Night Shift (00:00 to 8:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 0, 1 ) . $slot->printModifyButton(0,1,$week) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 0, 2 ) . $slot->printModifyButton(0,2,$week) . "</td>";
	print "</tr><tr class='r2'><td>Shadow</td>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 0, 3 ) . $slot->printModifyButton(0,3,$week) . "</td>";
		
	print "</tr><tr class='r1'><th rowspan='2'>Day Shift (8:00 to 16:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 1, 1 ) . $slot->printModifyButton(1,1,$week) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 1, 2 ) . $slot->printModifyButton(1,2,$week) . "</td>";
	print "</tr><tr class='r2'><td>Shadow</td>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 1, 3 ) . $slot->printModifyButton(1,3,$week) . "</td>";
		
	print "</tr><tr class='r1'><th rowspan='2'>Afternoon Shift (16:00 to 24:00)</th>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 2, 1 ) . $slot->printModifyButton(2,1,$week) . "</td>";
	print "</tr><tr class='r2'>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 2, 2 ) . $slot->printModifyButton(2,2,$week) . "</td>";
	print "</tr><tr class='r2'><td>Shadow</td>";
	foreach ( $slots as $slot )
		print "<td>" . $slot->printSlot ( 2, 3 ) . $slot->printModifyButton(2,3,$week) . "</td>";
		
	print "</tr></table>";
}

$error = False;
if(isset($_POST["view"]) && $_POST["view"]=="mod_slot"){
	$slotID1 = $_POST ["slot_id1"];
	$sh1_name = $_POST ["shifter_name1"];
	$institute1 = $_POST ["institute1"];
	
	$slotID2 = $_POST ["slot_id2"];
	$sh2_name = $_POST ["shifter_name2"];
	$institute2 = $_POST ["institute2"];
	
	$canceled = isset ( $_POST ["canceled"] );
	$date = $_POST ["date"];
	$slot = $_POST ["slot"];
	$type = $_POST ["type"];
	
	if ($_POST ["submit"] == "Delete") {
		if(!empty($slotID1))
			deleteSlot($db, $slotID1);
		if(!empty($slotID2))
			deleteSlot($db, $slotID2);
	} else {
		
		
		$shifterID1 = getUserID ( $db, "%", $sh1_name );
		$shifterID2 = getUserID ( $db, "%", $sh2_name );
		
		if ($shifterID1 == - 1){
			print "<div style='color:Red'>Shifter " . $sh1_name . " was not found.</div>";
			$error = True;
		}
		else {
			if (empty ( $slotID1 )) {
				// Create new assignment
				$shiftID = getShiftID ( $db, $date, $slot );
				if ($shiftID != - 1){
					createSlot ( $db, $shiftID, $shifterID1, $institute1, $type, $canceled );
				}
			} else
				modifySlot ( $db, $slotID1, $shifterID1, $institute1, $canceled );
		}
		if ($shifterID2 == - 1 && ! empty ( $sh2_name )){
			print "<div style='color:Red'>Shifter " . $sh2_name . " was not found.</div>";
			$error = True;
		}
		elseif (empty($sh2_name)){}
		else {
			if (empty ( $slotID2 )) {
				// Create new assignment
				$shiftID = getShiftID ( $db, $date, $slot );
				if ($shiftID != - 1){
					createSlot ( $db, $shiftID, $shifterID2, $institute2, $type, $canceled );
				}
			} else
				modifySlot ( $db, $slotID2, $shifterID2, $institute2, $canceled );
		}
	}
}
elseif(isset($_POST["view"]) && $_POST["view"]=="mod_comment"){
	$comment = $_POST["week_comment"];
	$week = $_POST["week_num"];
	
	$weekID = getWeekCommentID($db, $week);
	updateWeekComment($db, $weekID, $week, $comment);
}
?>
	<h1>Welcome to the NA62 shifts schedule administration website.</h1>
	<div style='text-align:center'>Last updated on <?php echo getLastUpdate();?></div>
<?php
for($week = 1; $week <= 30; $week ++) {
	buildTable ( $db, "2016-04-25", $week );
}
?>

<div class="search-form floating_window" style="width:450px;display:<?php echo (isset($_POST["view"])) ? 'block' : 'none'?>" id="mod_div">
	<h3 style="display:inline">Modify slot</h3><a style="margin-left: 320px" onclick="hideModify();">hide</a>
	<form id='formModify' action="shifts_admin.php" method="POST">
	<input type="hidden" id="view" name="view" value="mod_slot">
	<input type="hidden" id="date" name="date" value="<?php echoIfSet("date");?>">
	<input type="hidden" id="slot" name="slot" value="<?php echoIfSet("slot");?>">
	<input type="hidden" id="type" name="type" value="<?php echoIfSet("type");?>">
	<input type="hidden" id="slot_id1" name="slot_id1" value="<?php echoIfSet("slot_id1");?>">
	<input type="hidden" id="slot_id2" name="slot_id2" value="<?php echoIfSet("slot_id2");?>">
	<?php 
	$checked = "";
	if(isset($_POST["canceled"]))
		$checked = "checked";
	?>
	<table>
		<tr><td style="width:200px">Shifter Name1: </td><td><input type="text" name="shifter_name1" id="shifter_name1" value="<?php echoIfSet("shifter_name1");?>"></td></tr>
		<tr><td>Institute1: </td><td><input type="text" name="institute1" id="institute1" value="<?php echoIfSet("institute1");?>"></td></tr>
		<tr><td>Shifter Name2: </td><td><input type="text" name="shifter_name2" id="shifter_name2" value="<?php echoIfSet("shifter_name2");?>"></td></tr>
		<tr><td>Institute2: </td><td><input type="text" name="institute2" id="institute2" value="<?php echoIfSet("institute2");?>"></td></tr>
		<tr><td>Canceled <input type="checkbox" name="canceled" id="canceled" <?php echo $checked;?>></td>
		<td><input type="submit" name="submit" value="Validate"> <input type="submit" name="submit" id="delete" value="Delete" style="display:none"></td></tr>
	</table>
	</form>
</div>
<?php 
if(!$error){
	echo "<script type='text/javascript'>hideModify();</script>";
}
?>
</body>
</html>