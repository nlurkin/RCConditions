<?php

error_reporting(E_ALL);
ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);

include("config.php");

//Init connection to DB
$serverName = $_na62dbHost;
$userName = $_na62dbUser;
$password = $_na62dbPassword;
$dbName = $_na62dbName;

$conn = new mysqli($serverName, $userName, $password, $dbName, 3306);
if($conn->connect_error){
	die("Connection failed: " . $conn->connect_error . "<br>");
}

function humanReadable($value, $units){
	$i=0;
//	echo $value." ".$i."<br>";
	while($value >= 1000 and $i<count($units)-1){
//		echo $value." ".$i." ".$units[$i]."<br>";
		$value /= 1000.;
		$i=$i+1;
	}
	
	return $value." ".$units[$i];
}

if(!isset($_GET['view']) || $_GET['view']=='' || $_GET['view']=='csv'){
    //Get data from DB
    $sql = "SELECT run.id, run.number, run.startcomment, runtype.runtypename, run.timestart, run.timestop, viewtriggerfull.triggerstring, 
        viewenableddet.enabledstring
        FROM run 
        LEFT JOIN runtype ON (runtype.id = run.runtype_id)
        LEFT JOIN viewenableddet ON (viewenableddet.run_id = run.id)
        LEFT JOIN viewtriggerfull ON (run.id = viewtriggerfull.run_id)
        GROUP BY run.id
        ORDER BY run.number";
    $result = $conn->query($sql);
    //Fill the array with data
    if($result->num_rows >0){
    	$jsonArray = Array();
    	while($row = $result->fetch_assoc()){
    	    array_push($jsonArray, $row);
    	}
    }
    else{
        die("No data in database");
    }
}

//CSV view
if(isset($_GET['view']) && $_GET['view']=="csv"){
    header('Content-disposition: attachment; filename=na62_runlist.csv');
    header('Content-type: text/plain');
    
    if(count($jsonArray) >0){
		echo "Run #;Type;Start;End;Trigger(Downscaling);Start comment;Detectors;End comment\n";	
    	foreach($jsonArray as $row){
    	    $trigger = trim($row['triggerstring'], '+');
	        echo $row['number'].";".$row['runtypename'].";".$row['timestart'].";".$row['timestop'].";".$trigger.";".$row['startcomment'].";".$row['totalburst'].";".$row['totalL0'].";".$row['enabledstring'].";".$row['endcomment']."\n";
	    }
    }
}
else if(isset($_GET['view']) && $_GET['view']=="submitcomment"){
    $run_id = $_POST['run_id'];
    $comment = $_POST['comment'];
    
    //Update data in DB
    if( !($sql = $conn->prepare("UPDATE run SET run.usercomment=? WHERE run.id=?"))){
        echo "Prepare failed: (" . $conn->errno.") " . $conn->error;
    }
    
    if(!$sql->bind_param("si", $comment, $run_id)){
        echo "Binding parameters failed: (" . $sql->errno . ") ".$sql->error;
    }
    
    if(!$sql->execute()){
        echo "Execute failed: (" . $sql->errno . ") ".$sql->error;
    }
    header("Location:na62_runlist.php?view=details&run_id=".$run_id);
    die();
}
else if(isset($_GET['view']) && $_GET['view']=="downxml"){
	$sql = "SELECT run.number FROM run WHERE run.id=".$_GET['run_id'];
	$result = $conn->query($sql);


	if($result->num_rows >0){
		$dbres = $result->fetch_assoc();
	}
	else{
	    die("No data in database");
	}
	$file_name = $dbres['number'].'.xml';
	$file_url = 'http://nlurkinsql.cern.ch/XML/'.$file_name;
   header('Content-type: text/plain');
	header("Content-disposition: attachment; filename=\"".$file_name."\""); 
	readfile($file_url);
	exit;
}
else{
?>
    <html>
    <head>
    <title>NA62 Run Infos</title>
    <link rel="stylesheet" type="text/css" href="na62.css">
	<link rel="stylesheet" type="text/css" href="collapse.css">
	<script src="https://code.jquery.com/jquery-1.11.2.min.js"></script>
	<script src="https://code.jquery.com/ui/1.11.2/jquery-ui.min.js"></script>
	<script type="text/javascript" src="drag_collapse.js"></script>
    </head>
    <body>
<?php
    if(!isset($_GET['view']) || $_GET['view']==""){
?>
    <a href="na62_runlist.php?view=csv">Download as CSV file</a>
    <br>
    <br><b>Primitive triggers are not displayed.</b>
    <br><b>Click on a run number to add offline comment on the run</b>
    <table border=1 style="table-layout:fixed;">
        <tr>
            <th width='50px'>Run #</th>
            <th width='80px'>Type</th>
            <th width='150px'>Start</th>
            <th width='150px'>End</th>
            <th width='380px'>Detectors</th>
				<th width='*'>Start run comment</th>
            <th width='*' style='text-align:right'>Trigger/Downscaling(Reference)</th>
            <th width='50px'></th>
            <th width='50px'></th>
<!--            <th width='400px'>Start comment</th>
        </tr>
        <tr>
            <th colspan=1></th>
            <th># bursts</th>
            <th># L0</th>
            
            <th>End comment</th>
        </tr>
        <tr>
            <th colspan=5></th>
            <th>Offline comment</th>-->
        </tr>
<?php
    if(count($jsonArray) >0){
	    $i=0;
	    $css = Array("r1", "r2");
	    foreach($jsonArray as $row){
            $trigger = trim($row['triggerstring'], '+');
            echo "<tr class='d0 ".$css[$i%2]."' id='".$row['id']."'><td>".$row['number']."</td><td>".$row['runtypename']."</td><td>".$row['timestart']."</td><td>".$row['timestop']."</td><td class='wrappable'>".$row['enabledstring']."</td><td style='text-align:right' class='wrappable'>".$row['startcomment']."</td><td style='text-align:right' class='wrappable'>".$trigger."</td><td><a href='na62_runlist.php?view=details&run_id=".$row['id']."'>Details</a></td>";
				echo "<td><a href='na62_runlist.php?view=downxml&run_id=".$row['id']."'>XML</a></td>";
				echo "</tr>\n";
            $i++;
	    }
    }
?>
    </table>
<?php
    //End of table view
    }
    else if($_GET['view']=="details"){
		//Get data from DB
		$sql = "SELECT run.id, run.number, runtype.runtypename, run.timestart, run.timestop,
		    run.startcomment, run.endcomment, run.totalburst, run.totalL0, run.usercomment
		    FROM run 
		    LEFT JOIN runtype ON (runtype.id = run.runtype_id)
		    where run.id=".$_GET['run_id'];
		$result = $conn->query($sql);
		//Fill the array with data
		if($result->num_rows >0){
			$mainrow = $result->fetch_assoc();
		}
		else{
		    die("No data in database");
		}
?>
	<h1>Details for Run# <?php echo $mainrow['number']?></h1><a href="na62_runlist.php#<?php echo $_GET['run_id']?>" class="back">Back</a><br>
	<div class="subtitle">Click on the arrow on the right of a box to collapse/expand it.</div>
	<div class="column" id="col1">
		<div class="dragbox" id="boxShifter">
			<h2>Shifter information</h2><div class="collapsep">&#x25C0</div><div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr><td>Run Type</td><td><?php echo $mainrow['runtypename']?></td></tr>
					<tr><td>Start Time</td><td><?php echo $mainrow['timestart']?></td></tr>
					<tr><td>End Time</td><td><?php echo $mainrow['timestop']?></td></tr>
					<tr><td>Start Run comment</td><td><?php echo $mainrow['startcomment']?></td></tr>
					<tr><td>End Run comment</td><td><?php echo $mainrow['endcomment']?></td></tr>
					<tr><td>Offline comment <br><a href="na62_runlist.php?view=comment&run_id=<?php echo $mainrow['id']?>">Edit</a></td><td><?php echo $mainrow['usercomment']?></td></tr>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>Periodic Trigger<p>*EOR=End Of Run</p></h2><div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
			<div class="dragbox-content" style="display:none;">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr>
						<th width="150px">Frequency</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?
					$sql = "SELECT viewperiodic.validitystart, viewperiodic.validityend, viewperiodic.period
						FROM viewperiodic WHERE run_id=".$_GET['run_id']." ORDER BY validitystart";
					$result = $conn->query($sql);
					//Fill the array with data
					if($result->num_rows >0){
    					while($row = $result->fetch_assoc()){
    						if($row["validityend"]=="") $end = "EOR";
    						else $end=$row["validityend"]; 
    						$period = $row["period"]*1000000.;
    						$units = Array("Hz", "kHz", "MHz");
				    	    echo "<tr><td>".humanReadable($period, $units)."</td><td>".$row["validitystart"]."</td><td>".$end."</td></tr>";
				    	}
				    }
				?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>Calibration Trigger<p>*EOR=End Of Run</p></h2><div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
			<div class="dragbox-content" style="display:none;">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?
					$sql = "SELECT viewcalibration.validitystart, viewcalibration.validityend
						FROM viewcalibration WHERE run_id=".$_GET['run_id']." ORDER BY validitystart";
					$result = $conn->query($sql);
					//Fill the array with data
					if($result->num_rows >0){
    					while($row = $result->fetch_assoc()){
    						if($row["validityend"]=="") $end = "EOR";
    						else $end=$row["validityend"]; 
				    	    echo "<tr><td>".$row["validitystart"]."</td><td>".$end."</td></tr>";
				    	}
				    }
				?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>NIM Trigger<p>*EOR=End Of Run</p></h2><div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
			<div class="dragbox-content" style="display:none;">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr>
						<th width="50px">Mask</th>
						<th width="200px">Trigger</th>
						<th width="50px">Downs.</th>
						<th width="55px">Ref. Det.</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?
					$sql = "SELECT DISTINCT viewnimtype.validitystart, viewnimtype.validityend, viewnimtype.mask, 
								viewnimtype.triggernimdownscaling, viewnimtype.triggernimreference, 
								viewnimname.det_0, viewnimname.det_1, viewnimname.det_2, viewnimname.det_3, viewnimname.det_4
						FROM viewnimtype 
						LEFT JOIN viewnimname ON (viewnimtype.nim_id = viewnimname.nim_id)
						WHERE viewnimtype.run_id=".$_GET['run_id']." ORDER BY validitystart";
					$result = $conn->query($sql);
					//Fill the array with data
					if($result->num_rows >0){
    					while($row = $result->fetch_assoc()){
    						if($row["validityend"]=="") $end = "EOR";
    						else $end=$row["validityend"];
    						$string = "";
    						for($i=0;$i<=4; $i++){
    							if($string=="") $string=$row["det_".$i];
    							elseif($row["det_".$i]!="") $string=$string."*".$row["det_".$i];
    						}
				    	    echo "<tr><td>".$row["mask"]."</td><td>".$string."</td><td>".$row["triggernimdownscaling"]."</td><td>".$row["triggernimreference"]."</td><td>".$row["validitystart"]."</td><td>".$end."</td></tr>";
				    	}
				    }
				?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>Primitive Trigger<p>*EOR=End Of Run</p></h2><div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
			<div class="dragbox-content" style="display:none;">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr>
						<th width="60px">Mask</th>
						<th width="60px">Downs.</th>
						<th width="60px">Ref. Det.</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?
					$sql = "SELECT DISTINCT viewprimitivetype.validitystart, viewprimitivetype.validityend, viewprimitivetype.mask, 
								viewprimitivetype.triggerprimitivedownscaling, viewprimitivetype.triggerprimitivereference
						FROM viewprimitivetype 
						WHERE viewprimitivetype.run_id=".$_GET['run_id']." ORDER BY validitystart";
					$result = $conn->query($sql);
					//Fill the array with data
					if($result->num_rows >0){
    					while($row = $result->fetch_assoc()){
    						if($row["validityend"]=="") $end = "EOR";
    						else $end=$row["validityend"];
				    	    echo "<tr><td>".$row["mask"]."</td><td>".$row["triggerprimitivedownscaling"]."</td><td>".$row["triggerprimitivereference"]."</td><td>".$row["validitystart"]."</td><td>".$end."</td></tr>";
				    	}
				    }
				?>
				</table>
			</div>
		</div>
	</div>
	<div class="column" id="col2">
		<div class="dragbox" id="boxCollected">
			<h2>Collected information</h2><div class="collapsep">&#x25C0</div><div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr><td>Run Number</td><td><?php echo $mainrow['number']?></td></tr>
					<tr><td>Number of Bursts</td><td><?php echo $mainrow['totalburst']?></td></tr>
					<tr><td>Number of L0</td><td><?php echo $mainrow['totalL0']?></td></tr>
					<tr><td>Number of L1</td><td><?php echo $mainrow['totalL1']?></td></tr>
					<tr><td>Number of L2</td><td><?php echo $mainrow['totalL2']?></td></tr>
				</table>
			</div>
		</div>
		<div class="dragbox" id="boxDetector">
			<h2>Enabled Detectors<p>*EOR=End Of Run</p></h2><div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
			<div class="dragbox-content" style="display:none;">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr>
						<th width="100px">Detector</th>
						<th width="80px">Source ID</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?
					$sql = "SELECT enableddetectors.detectorid, enableddetectors.detectorname, 
						enableddetectors.validitystart, enableddetectors.validityend
						FROM enableddetectors WHERE run_id=".$_GET['run_id']." ORDER BY validitystart";
					$result = $conn->query($sql);
					//Fill the array with data
					if($result->num_rows >0){
    					while($row = $result->fetch_assoc()){
    						if($row["validityend"]=="") $end = "EOR";
    						else $end=$row["validityend"]; 
				    	    echo "<tr><td>".$row["detectorname"]."</td><td>".$row["detectorid"]."</td><td>".$row["validitystart"]."</td><td>".$end."</td></tr>";
				    	}
				    }
				?>
				</table>
			</div>
		</div>
	<div>
<?php
    }
    else if($_GET['view']=="comment"){
        //Get data from DB
        $sql = "SELECT run.id, run.number, run.usercomment
            FROM run WHERE run.id=".$_GET['run_id'];
        $result = $conn->query($sql);
        //Fill the array with data
        if($result->num_rows >0){
            $row = $result->fetch_assoc();
        }
?>
    Add a comment for run <?php echo $row['number'];?>
    <form action="na62_runlist.php?view=submitcomment" method="POST">
        <input type="hidden" name="run_id" value="<?php echo $_GET['run_id']?>" >
        <textarea name="comment" cols=100 rows=10><?php echo $row['usercomment']?></textarea><br>
        <input type="submit" value="submit">
    </form>
<?php
    //End of comment view 
    }
?>
    </body>
    </html>
<?php
//End of display views
}

//Close connection to DB
$conn->close();
?>
