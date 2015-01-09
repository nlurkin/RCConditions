<?php

//Init connection to DB
$serverName = "nlurkinsql.cern.ch";
$userName = "***REMOVED***";
$password = "***REMOVED***";
$dbName = "testRC";

$conn = new mysqli($serverName, $userName, $password, $dbName, 3306);
if($conn->connect_error){
	die("Connection failed: " . $conn->connect_error . "<br>");
}

if($_GET['view']=='' || $_GET['view']=='csv'){
    //Get data from DB
    $sql = "SELECT run.id, run.number, runtype.runtypename, run.timestart, run.timestop, viewtriggerfull.triggerstring, 
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
if($_GET['view']=="csv"){
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
else if($_GET['view']=="submitcomment"){
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
    header("Location:na62_runlist.php");
    die();
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
    if($_GET['view']==""){
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
            <th width='450px'>Detectors</th>
            <th width='*' style='text-align:right'>Trigger/Downscaling(Reference)</th>
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
            echo "<tr class='d0 ".$css[$i%2]."'><td>".$row['number']."</td><td>".$row['runtypename']."</td><td>".$row['timestart']."</td><td>".$row['timestop']."</td><td class='wrappable'>".$row['enabledstring']."</td><td style='text-align:right' class='wrappable'>".$trigger."</td><td><a href='na62_runlist.php?view=details&run_id=".$row['id']."'>Details</a></td>";
            //<td>".$row['startcomment']."</td></tr>\n";
            //echo "<tr class='d1 ".$css[$i%2]."'><td colspan=1></td><td>".$row['totalburst']."</td><td>".$row['totalL0']."</td><td colspan=2>".$row['enabledstring']."</td><td>".$row['endcomment']."</td></tr>\n";
            //echo "<tr class='d1 ".$css[$i%2]."'><td colspan=5></td><td>".$row['usercomment']."</td></tr>\n";
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
		$sql = "SELECT run.id, run.number, runtype.runtypename, run.timestart, run.timestop, viewtriggerfull.triggerstring, 
		    viewenableddet.enabledstring, run.startcomment, run.endcomment, run.totalburst, run.totalL0, run.usercomment
		    FROM run 
		    LEFT JOIN runtype ON (runtype.id = run.runtype_id)
		    LEFT JOIN viewenableddet ON (viewenableddet.run_id = run.id)
		    LEFT JOIN viewtriggerfull ON (run.id = viewtriggerfull.run_id)
		    where run.id=".$_GET['run_id'];
		$result = $conn->query($sql);
		//Fill the array with data
		if($result->num_rows >0){
			$row = $result->fetch_assoc();
		}
		else{
		    die("No data in database");
		}
?>
	<h1>Details for Run# <? echo $row['number']?></h1>
	<div class="column" id="col1">
		<div class="dragbox" id="box1">
			<h2>Global information</h2><div class="collapsep">&#x25C0</div><div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr><td>Run #</td><td><?php echo $row['number']?></td></tr>
					<tr><td>Start Time</td><td><?php echo $row['timestart']?></td></tr>
					<tr><td>End Time</td><td><?php echo $row['timestop']?></td></tr>
					<tr><td>Start Run comment</td><td><?php echo $row['startcomment']?></td></tr>
					<tr><td>End Run comment</td><td><?php echo $row['endcomment']?></td></tr>
				</table>
			</div>
		</div>
	</div>
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
