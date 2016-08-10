<?php
function toSQLDate($ts) {
	return date ( "Y-m-d", $ts );
}
function toSQLDateTime($ts) {
	return date ( "Y-m-d H:i:s", $ts );
}
class Slot {
	public $canceled = False;
	public $sh1 = Array ();
	public $institute1 = Array ();
	public $sh1_id = Array ();
	public $sh2 = Array ();
	public $institute2 = Array ();
	public $sh2_id = Array ();
	public $sh3 = Array();
	public $sh3_id = Array();
	
	function __construct($canceled) {
		$this->canceled = $canceled;
	}
	public function addShifter($num, $sh, $institute, $id) {
		if ($num == 1) {
			array_push ( $this->sh1, $sh );
			array_push ( $this->institute1, $institute );
			array_push ( $this->sh1_id, $id );
		} elseif ($num == 2) {
			array_push ( $this->sh2, $sh );
			array_push ( $this->institute2, $institute );
			array_push ( $this->sh2_id, $id );
		} elseif( $num ==3 ) {
			array_push ( $this->sh3, $sh );
			array_push ( $this->sh3_id, $id );
		}
	}
	public function printShifter($sh) {
		$retString = "";
		$cancelString = "";
		if ($this->canceled)
			$cancelString = "<font style='color:red'>  -  Canceled</font>";
		if ($sh == 1) {
			if(sizeof($this->sh1)>0){
				$retString = $retString . "Sh1" . $cancelString . "<br>";
				foreach ( $this->sh1 as $index => $shifter )
					$retString = $retString . $this->institute1 [$index] . " " . $shifter . "<br>";
			}
		} elseif ($sh == 2) {
			if(sizeof($this->sh2)>0){
				$retString = $retString . "Sh2" . $cancelString . "<br>";
				foreach ( $this->sh2 as $index => $shifter )
					$retString = $retString . $this->institute2 [$index] . " " . $shifter . "<br>";
			}
		} elseif ($sh == 3) {
			if(sizeof($this->sh3)>0){
				$retString = implode(", ", $this->sh3);
			}
		}
		return $retString;
	}
	
	public function printModifyButton($sh, $date, $slot, $week){
		$sh_id = "";
		$sh_inst = "";
		$sh_name = "";
		$type = "";
		$empty = false;
		if( $sh==1){
			$sh_id = "[\"" . implode("\",\"",$this->sh1_id) . "\"]";
			$sh_inst = "[\"" . implode("\",\"",$this->institute1) . "\"]";
			$sh_name = "[\"" . implode("\",\"",$this->sh1) . "\"]";
			$type = 1;
			if(sizeof($this->sh1_id)==0) $empty= true;
		}
			elseif( $sh==2){
			$sh_id = "[\"" . implode("\",\"",$this->sh2_id) . "\"]";
			$sh_inst = "[\"" . implode("\",\"",$this->institute2) . "\"]";
			$sh_name = "[\"" . implode("\",\"",$this->sh2) . "\"]";
			$type = 2;
			if(sizeof($this->sh2_id)==0) $empty= true;
		}
		elseif( $sh==3){
			$sh_id = "[\"" . implode("\",\"",$this->sh3_id) . "\"]";
			$sh_inst = "[\"\",\"\"]";
			$sh_name = "[\"" . implode("\",\"",$this->sh3) . "\"]";
			$type = 3;
			if(sizeof($this->sh3_id)==0) $empty= true;
		}
		if(!$empty){
			$buttonString = "<input class='shifts' type='button' value='Modify' onClick='modifyID(" . $sh_id 
					. ",". $sh_inst . "," . str_replace("'", "$", $sh_name) . ",". $this->canceled . ",\"". $date . "\"," 
					. $slot . ",\"" . $type . "\", " . $week . ")'>";
		}
		else{
			$buttonString = "<input class='shifts' type='button' value='Create' onClick='modifyID([],[],"
					. "[],false,\"". $date . "\"," . $slot . ",\"" . $type . "\", " . $week . ")'>";
		}
		
		return $buttonString;
	}
}
class ShiftDay {
	public $date = 0;
	public $slots = Array ();
	function __construct($date) {
		$this->date = strtotime ( $date );
	}
	public function appendSlot($num, $canceled) {
		if (! array_key_exists ( $num, $this->slots ))
			$this->slots [$num] = new Slot ( $canceled );
	}
	public function addShifterToSlot($num, $shType, $sh, $institute, $id) {
		$this->slots [$num]->addShifter ( $shType, $sh, $institute, $id );
	}
	public function printSlot($num, $sh) {
		if (array_key_exists ( $num, $this->slots ))
			return $this->slots [$num]->printShifter ( $sh );
	}
	
	public function printModifyButton($num, $sh, $week){
		if (array_key_exists ( $num, $this->slots ))
			return $this->slots [$num]->printModifyButton ( $sh , $this->date, $num, $week);
		else 
			return "<input class='shifts' type='button' value='Create' onClick='modifyID([], [], [], false, \"" . $this->date . "\", ". $num . ", \"" . $sh . "\", " . $week . ")'>";
	}
}
function getShiftsFromTo($db, $from, $to) {
	$sql = "SELECT * FROM shifts_display WHERE date>='" . toSQLDate ( $from ) . "' AND date<='" . toSQLDate ( $to ) . "' ORDER BY date";
	$db->executeGet ( $sql );
	
	$slots = Array ();
	$currentDate = NULL;
	$currentDay = NULL;
	while ( $row = $db->next () ) {
		if ($currentDate === NULL || $currentDate != $row ["date"]) {
			if ($currentDate !== NULL)
				array_push ( $slots, $currentDay );
			$currentDay = new ShiftDay ( $row ["date"] );
			$currentDate = $row ["date"];
		}
		$currentDay->appendSlot ( $row ["slot"], $row ["canceled"] );
		if ($row ["shift_type"] == 1) {
			$currentDay->addShifterToSlot ( $row ["slot"], 1, $row ["surname"], $row ["institute"], $row ["id"] );
		} elseif ($row ["shift_type"] == 2) {
			$currentDay->addShifterToSlot ( $row ["slot"], 2, $row ["surname"], $row ["institute"], $row ["id"] );
		} elseif ($row ["shift_type"] == 3) {
			$currentDay->addShifterToSlot ( $row ["slot"], 3, $row ["surname"], "", $row ["id"] );
		}
	}
	
	array_push ( $slots, $currentDay );
	return $slots;
}

function modifySlot($db, $shiftID, $shifterID, $institute, $type, $canceled){
	$db->executeUpdate("INSERT INTO shifts_assignments (shift_id, shifter_id, shift_type, institute, canceled) VALUES (?,?,?,?,?)", "iiisi", $shiftID, $shifterID, $type, $institute, $canceled);
	$db->executeUpdate("UPDATE shifts_assignments SET canceled=? WHERE shift_id=?", "ii", $canceled, $shiftID);
	updateLastUpdate();
}

function createSlot($db, $shiftID, $shifterID, $institute, $type, $canceled){
	$db->executeUpdate("INSERT INTO shifts_assignments (shift_id, shifter_id, shift_type, institute, canceled) VALUES (?,?,?,?,?)", "iiisi", $shiftID, $shifterID, $type, $institute, $canceled);
	updateLastUpdate();
}

function deleteSlot($db, $slotID){
	$db->executeUpdate("DELETE FROM shifts_assignments WHERE id=?", "i", $slotID);
	updateLastUpdate();
}

function getShiftID($db, $date, $slot){
	$db->executeGet("SELECT id FROM shifts WHERE date='" .toSQLDate($date) . "' AND slot=" . $slot);
	if($row = $db->next()){
		return $row["id"];
	}
	return -1;
}

function getWeekCommentID($db, $week){
	$db->executeGet("SELECT id FROM week_comments WHERE week_num=".$week);
	if($row = $db->next()){
		return $row["id"];
	}
	return -1;
}

function getWeekComment($db, $week, $format){
	$db->executeGet("SELECT comment FROM week_comments WHERE week_num=" . $week . " ORDER BY version_date DESC");
	if($row = $db->next()){
		if($format)
			return "<div style='color:Red'>" . $row["comment"] . "</div>";
		else 
			return $row["comment"];
	}
	return "";
}

function updateWeekComment($db, $weekID, $week, $comment){
	$db->executeUpdate("INSERT INTO week_comments (week_num, comment) VALUES (?,?)", "is", $week, $comment);
	updateLastUpdate();
}
function getLastUpdate($prefix=""){
	$val = stat($prefix . "touchdir/shifts_schedule_lastUpdate.php");
	$time = $val["mtime"];
	return strftime("%Y-%m-%d %H:%M:%S", $time);
}
function updateLastUpdate(){
	touch("../touchdir/shifts_schedule_lastUpdate.php");
}
?>
