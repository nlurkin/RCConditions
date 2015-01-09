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
        viewenableddet.enabledstring, run.startcomment, run.endcomment, run.totalburst, run.totalL0, run.usercomment
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
    <style>
    table {
	    font: 11px/24px Verdana, Arial, Helvetica, sans-serif;
	    border-collapse: collapse;
	    width: 100%;
	    }

    th {
	    border-top: 1px solid #FB7A31;
	    border-bottom: 1px solid #FB7A31;
	    background: #FFC;
	    }
    tr.d0 {

    }
    tr.d1 {

    }

    tr.r1 {
	    background-color: #b8d1f3;
    }
    tr.r2 {
	    background-color: #dae5f4;
    }

    td {
	    border-bottom: 1px solid #CCC;
	    padding: 0 0.5em;
	    }
    </style>
    </head>
    <body>
<?php
    if($_GET['view']==""){
?>
    <a href="na62_runlist.php?view=csv">Download as CSV file</a>
    <br>
    <br><b>Primitive triggers are not displayed.</b>
    <br><b>Click on a run number to add offline comment on the run</b>
    <table border=1>
        <tr>
            <th width='60px'>Run #</th>
            <th width='150px'>Type</th>
            <th width='150px'>Start</th>
            <th width='150px'>End</th>
            <th width='250px' style='text-align:right'>Trigger(Downscaling)</th>
            <th width='400px'>Start comment</th>
        </tr>
        <tr>
            <th colspan=1></th>
            <th># bursts</th>
            <th># L0</th>
            <th colspan=2>Detectors</th>
            <th>End comment</th>
        </tr>
        <tr>
            <th colspan=5></th>
            <th>Offline comment</th>
        </tr>
<?php
    if(count($jsonArray) >0){
	    $i=0;
	    $css = Array("r1", "r2");
	    foreach($jsonArray as $row){
            $trigger = trim($row['triggerstring'], '+');
            echo "<tr class='d0 ".$css[$i%2]."'><td><a href='na62_runlist.php?view=comment&run_id=".$row['id']."'>".$row['number']."</a></td><td>".$row['runtypename']."</td><td>".$row['timestart']."</td><td>".$row['timestop']."</td><td style='text-align:right'>".$trigger."</td><td>".$row['startcomment']."</td></tr>\n";
            echo "<tr class='d1 ".$css[$i%2]."'><td colspan=1></td><td>".$row['totalburst']."</td><td>".$row['totalL0']."</td><td colspan=2>".$row['enabledstring']."</td><td>".$row['endcomment']."</td></tr>\n";
            echo "<tr class='d1 ".$css[$i%2]."'><td colspan=5></td><td>".$row['usercomment']."</td></tr>\n";
            $i++;
	    }
    }
?>
    </table>
<?
    //End of table view
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
