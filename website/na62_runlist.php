<?php
// Error handling
error_reporting(E_ALL);
ini_set('display_errors', TRUE);
ini_set('display_startup_errors', TRUE);

// Get site specific configuration
include("config.php");
include("na62_helper.php");
include("na62_fetch.php");

// Define some global variables
$frequencyUnits = Array("Hz", "kHz", "MHz");
$db = new DBConnect();
$dataArray = Array();

if(!$db->init($_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort)){
	die("Connection failed: " . $db->getError() . "<br>");
}

// Get data from Database
if(!isset($_GET['view']) || $_GET['view']=='' || $_GET['view']=='csv'){
	$dataArray = fetch_all($db);
}
else if(isset($_GET['view']) && $_GET['view']=="search"){
	$runLimits = 100;
	$rowOffset = 0;
	if(isset($_GET['page'])) $rowOffset = $_GET['page']*runLimits;
	$currentPage = $rowOffset/$runLimits;
	
	$searchParams = Array();
	if(isset($_GET["run_from"]) && !empty($_GET["run_from"])) $searchParams["run_from"] = $_GET["run_from"];
	if(isset($_GET["run_to"]) && !empty($_GET["run_to"])) $searchParams["run_to"] = $_GET["run_to"];
	if(isset($_GET["date_from"]) && !empty($_GET["date_from"])) $searchParams["date_from"] = $_GET["date_from"];
	if(isset($_GET["date_to"]) && !empty($_GET["date_to"])) $searchParams["date_to"] = $_GET["date_to"];
	if(isset($_GET["detectors_en"])) $searchParams["detectors_en"] = $_GET["detectors_en"];
	$sqlwhere = generate_search_sql($searchParams);
	$dataArray = fetch_search($db, $rowOffset, $runLimits, $sqlwhere);
	
	$nPages = (int)(fetch_nRuns($db, $sqlwhere)/$runLimits)+1;
}

// Display data
// CSV view
if(isset($_GET['view']) && $_GET['view']=="csv"){
    header('Content-disposition: attachment; filename=na62_runlist.csv');
    header('Content-type: text/plain');
    
    if(count($dataArray) >0){
		echo "Run #;Type;Start;End;Trigger(Downscaling);Start comment;Detectors;End comment\n";	
    	foreach($dataArray as $row){
			$triggerstring = trim($row['triggerstring'], '+');
			$enabledstring = $row['enabledstring'];
	        echo $row['number'].";".$row['runtypename'].";".$row['timestart'].";".$row['timestop'].";".$triggerstring.";".$row['startcomment'].";".$enabledstring.";".$row['endcomment']."\n";
	    }
    }
}
// Comment view (submit - no display)
else if(isset($_GET['view']) && $_GET['view']=="submitcomment"){
    $run_id = $_POST['run_id'];
    $comment = $_POST['comment'];

	$sql = "UPDATE run SET run.usercomment=? WHERE run.id=?";
	if($db->executeUpdate($sql, "si", $comment, $run_id)){
		header("Location:na62_runlist.php?view=details&run_id=".$run_id);
	}
    die();
}
// Download XML view
else if(isset($_GET['view']) && $_GET['view']=="downxml"){
	$dbres = fetch_xml($db, $_GET['run_id']);
	$file_name = $dbres['number'].$_na62XmlExtension;
	$file_url = $_na62XmlAddress.$file_name;
	header('Content-type: '.$_na62XmlMIMEType);
	header("Content-disposition: attachment; filename=\"".$file_name."\""); 
	readfile($file_url);
	exit;
}
// Multi-run table views (normal and search)
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
    if(!isset($_GET['view']) || $_GET['view']=="" || $_GET['view']=="search"){
?>
	<h1>NA62 Run Conditions Database</h1>
	<div style="text-align:center; max-width:600px;margin:0 auto;">This page displays the list of runs recorded by the RunControl. This is only an extract of all the information present in the RunControl database. This list can be <a href="na62_runlist.php?view=csv">Downloaded as CSV file</a></div>
	<div style="width:1100px">
	<ul>
	<li><b>The triggers are given with their downscaling (/ symbol) and the reference detector for the timing (in the parenthesis).</b>
    <li><b>Click on the "Details" link to see more details about the run (trigger and enabled detectors timeline and few other metadata).</b>
	<b>You can also add an offline comment to the run (good for x, bad for y, ...)</b>
	<li><b>The full set of values and events recorded by RunControl for the run (including board configuration) 
	is available for download by clicking the "XML" link. The XML format is explained <a href="xmlhelp.php">here</a>.</b>
	</ul>
	</div>
	<div class="search-form">
	<h4>Search</h4>
<?php
	if(isset($_GET["run_from"])) $run_from = $_GET["run_from"];
	else $run_from = "";
	if(isset($_GET["run_to"])) $run_to = $_GET["run_to"];
	else $run_to = "";
	if(isset($_GET["date_from"])) $date_from = $_GET["date_from"];
	else $date_from = "";
	if(isset($_GET["date_to"])) $date_to = $_GET["date_to"];
	else $date_to = "";
	
	$det_checked = array(
		"CHANTI" => "",
		"CHOD" => "",
		"GTK" => "",
		"IRC_SAC" => "",
		"KTAG" => "",
		"L0TP" => "",
		"LAV" => "",
		"LKR" => "",
		"MUV1" => "",
		"MUV3" => "",
		"RICH" => "",
		"STRAW" => ""
	);
	if(isset($_GET["detectors_en"])){
		foreach($_GET["detectors_en"] as $det) $det_checked[$det] = "checked";
	}
	if(isset($_GET['view']) && $_GET['view']=="search"){
?>
	<div class="collapsep">&#x25C0</div><div class="collapsem">&#9660</div>
	<div class="search-form-content">
<?php
	}else{
?>
	<div class="collapsep" style="display:inline;">&#x25C0</div><div class="collapsem" style="display:none;">&#9660</div>
	<div class="search-form-content" style="display: none;">
<?php
	}
?>
    <form action="na62_runlist.php" method="GET">
		<input type="hidden" name="view" value="search">
		
		<label class = "main" for="run_from"><span>Run number</span>
		<input type="number" class="input-field" name="run_from" id="run_from" 
			placeholder="From run #" value="<?php echo $run_from;?>">
		<input type="number" class="input-field" name="run_to"   id="run_to"   
			placeholder="To run #"   value="<?php echo $run_to;?>">
		</label>
		
		
		<label class = "main" for="date_from"><span>Date </span>
		<input type="text" class="input-field-date" name="date_from" id="date_from" 
			onfocus="(this.type='date')" onblur="(this.type='text')" placeholder="From date" 
			value="<?php echo $date_from;?>">
		<input type="text" class="input-field-date" name="date_to" id="date_to"
			onfocus="(this.type='date')" onblur="(this.type='text')" placeholder="To data"
			value="<?php echo $date_to;?>">
		</label>
		
		
		<label class = "main" for="detectors_en[]"><span>Enabled detectors</span>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[0]" 
				value="CHANTI"  <?php echo $det_checked["CHANTI"]; ?>>
			<label for="detectors_en[0]">CHANTI</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[1]" 
				value="CHOD"    <?php echo $det_checked["CHOD"]; ?>>
			<label for="detectors_en[1]">CHOD</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[2]" 
				value="GTK"     <?php echo $det_checked["GTK"]; ?>>
			<label for="detectors_en[2]">GTK</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[3]"
				value="IRC_SAC" <?php echo $det_checked["IRC_SAC"]; ?>>
			<label for="detectors_en[3]">IRC_SAC</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[4]"
				value="KTAG"   <?php echo $det_checked["KTAG"]; ?>>
			<label for="detectors_en[4]">KTAG</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[5]"
				value="L0TP"    <?php echo $det_checked["L0TP"]; ?>>
			<label for="detectors_en[5]">L0TP</label>
		<br>
		<span></span>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[6]"
				value="LAV"    <?php echo $det_checked["LAV"]; ?>>
			<label for="detectors_en[6]">LAV</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[7]"
				value="LKR"    <?php echo $det_checked["LKR"]; ?>>
			<label for="detectors_en[7]">LKr</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[8]"
				value="MUV1"   <?php echo $det_checked["MUV1"]; ?>>
			<label for="detectors_en[8]">MUV1&2</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[9]"
				value="MUV3"   <?php echo $det_checked["MUV3"]; ?>>
			<label for="detectors_en[9]">MUV3</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[10]"
				value="RICH"   <?php echo $det_checked["RICH"]; ?>>
			<label for="detectors_en[10]">RICH</label>
		<input type="checkbox" class="input-field-box" name="detectors_en[]" id="detectors_en[11]"
				value="STRAW"  <?php echo $det_checked["STRAW"]; ?>>
			<label for="detectors_en[11]">Straw</label>
		</label>
		<input type="submit" value="Search">
    </form>
	</div>
	</div>
	</div>
<?php
	if(isset($_GET['view']) && $_GET['view']=="search"){
?>
	<div style="text-align:right">
	Page:
	<?php if($rowOffset>0) {?><a href="na62_runlist.php?view=search&page=<?php echo $currentPage-1;?>">Prev</a><?php } ?>
<?php
	for($i = 0; $i<$currentPage+5 && $i<$nPages; $i++){
		if($i==$currentPage) echo ($i+1)." ";
		else echo '<a href="na62_runlist.php?view=search&page="'.$i.'">'.($i+1).'</a> ';
	}
?>
	<a href="na62_runlist.php?view=search&rowoffset=<?php echo $currentPage+1;?>">Next</a>
	</div>

<?php
	}
	else{
		echo "<br>";
	}
?>
    <table border=1 style="table-layout:fixed;">
        <tr>
            <th width='50px'>Run #</th>
            <th width='80px'>Type</th>
            <th width='150px'>Start</th>
            <th width='150px'>End</th>
            <th width='200px'>Detectors</th>
			<th width='300px'>Start run comment</th>
            <th width='*' style='text-align:right'>Trigger/Downscaling(Ref)</th>
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
    if(count($dataArray) >0){
	    $i=0;
	    $css = Array("r1", "r2");
	    foreach($dataArray as $row){
			if(!isset($_GET['view']) || $_GET['view']==""){
				$triggerstring = prepare_trigger("all", $row);
				$enabledstring = prepare_enabled("all", $row);
			}
			else if($_GET['view']=="search"){
				$enabledstring = prepare_enabled("search", $row);
				$triggerstring = prepare_trigger("search", $row);
			}
            echo "<tr class='d0 ".$css[$i%2]."' id='".$row['id']."'><td>".$row['number']."</td><td>".$row['runtypename']."</td><td>".$row['timestart']."</td><td>".$row['timestop']."</td><td class='wrappable'>".$enabledstring."</td><td style='text-align:right' class='wrappable'>".$row['startcomment']."</td><td style='text-align:right' class='wrappable'>".$triggerstring."</td><td><a href='na62_runlist.php?view=details&run_id=".$row['id']."'>Details</a></td>";

				$file_name = $row['number'].$_na62XmlExtension;
				$file_url = $_na62XmlAddress.$file_name;
				if(exists($file_url)){
					echo "<td><a href='na62_runlist.php?view=downxml&run_id=".$row['id']."'>XML</a></td>";
				}
				else{
					echo "<td></td>";
				}
				echo "</tr>\n";
            $i++;
	    }
    }
?>
    </table>
<?php
    //End of table views
    }
	// Run details view
    else if($_GET['view']=="details"){
		//Get data from DB
		$runDetails = fetch_run_details($db, $_GET['run_id']);
?>
	<h1>Details for Run# <?php echo $runDetails['number']?></h1><a href="na62_runlist.php#<?php echo $_GET['run_id']?>" class="back">Back</a><br>
	<div class="subtitle">Click on the arrow on the right of a box to collapse/expand it.</div>
	<div class="column" id="col1">
		<div class="dragbox" id="boxShifter">
			<h2>Shifter information</h2><div class="collapsep">&#x25C0</div><div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout:fixed; width:100%" class="autoalternate">
					<tr><td>Run Type</td><td><?php echo $runDetails['runtypename'];?></td></tr>
					<tr><td>Start Time</td><td><?php echo $runDetails['timestart'];?></td></tr>
					<tr><td>End Time</td><td><?php echo $runDetails['timestop'];?></td></tr>
					<tr><td>Start Run comment</td><td><?php echo $runDetails['startcomment'];?></td></tr>
					<tr><td>End Run comment</td><td><?php echo $runDetails['endcomment'];?></td></tr>
					<tr><td>Offline comment <br><a href="na62_runlist.php?view=comment&run_id=<?php echo $runDetails['id'];?>">Edit</a></td><td><?php echo $runDetails['usercomment'];?></td></tr>
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
				<?php
					foreach($runDetails["periodic"] as $periodic){
						if($periodic["validityend"]=="") $end = "EOR";
						else $end=$periodic["validityend"]; 
						$period = $periodic["frequency"]*1000000.;
						echo "<tr><td>".humanReadable($period, $frequencyUnits)."</td><td>".$periodic["validitystart"]."</td><td>".$end."</td></tr>";
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
				<?php
					foreach($runDetails["calibration"] as $calib){
						if($calib["validityend"]=="") $end = "EOR";
						else $end=$calib["validityend"]; 
						echo "<tr><td>".$calib["validitystart"]."</td><td>".$end."</td></tr>";
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
				<?php
					foreach($runDetails["nim"] as $nim){
						if($nim["validityend"]=="") $end = "EOR";
						else $end=$nim["validityend"];
						$string = "";
						for($i=0;$i<=4; $i++){
							if($string=="") $string=$nim["det_".$i];
							elseif($nim["det_".$i]!="") $string=$string."*".$nim["det_".$i];
						}
						echo "<tr><td>".$nim["mask"]."</td><td>".$string."</td><td>".$nim["triggernimdownscaling"]."</td><td>".$nim["triggernimreference"]."</td><td>".$nim["validitystart"]."</td><td>".$end."</td></tr>";
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
						<th width="120px">Trigger</th>
						<th width="60px">Downs.</th>
						<th width="60px">Ref. Det.</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
					//TODO improve
					foreach($runDetails["primitive"] as $prim){
						if($prim["validityend"]=="") $end = "EOR";
						else $end=$prim["validityend"];
						$primNameArr = Array();
						if(!is_null($prim["maskA"])) array_push($primNameArr, $prim["maskA"]);
						if(!is_null($prim["maskB"])) array_push($primNameArr, $prim["maskB"]);
						if(!is_null($prim["maskC"])) array_push($primNameArr, $prim["maskC"]);
						if(!is_null($prim["maskD"])) array_push($primNameArr, $prim["maskD"]);
						if(!is_null($prim["maskE"])) array_push($primNameArr, $prim["maskE"]);
						if(!is_null($prim["maskF"])) array_push($primNameArr, $prim["maskF"]);
						if(!is_null($prim["maskG"])) array_push($primNameArr, $prim["maskG"]);
						echo "<tr><td>&nbsp;</td><td>".implode("x", $primNameArr)."</td><td>".$prim["triggerprimitivedownscaling"]."</td><td>".$prim["triggerprimitivereference"]."</td><td>".$prim["validitystart"]."</td><td>".$end."</td></tr>";
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
					<tr><td>Run Number</td><td><?php echo $runDetails['number']?></td></tr>
					<tr><td>Number of Bursts</td><td><?php echo $runDetails['totalburst']?></td></tr>
					<tr><td>Number of L0</td><td><?php echo $runDetails['totalL0']?></td></tr>
					<tr><td>Number of L1</td><td><?php echo $runDetails['totalL1']?></td></tr>
					<tr><td>Number of L2</td><td><?php echo $runDetails['totalL2']?></td></tr>
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
				<?php
					foreach($runDetails["enableddetectors"] as $enabled){
						if($enabled["validityend"]=="") $end = "EOR";
						else $end=$enabled["validityend"]; 
						echo "<tr><td>".$enabled["detectorname"]."</td><td>".$enabled["detectorid"]."</td><td>".$enabled["validitystart"]."</td><td>".$end."</td></tr>";
					}
				?>
				</table>
			</div>
		</div>
	<div>
<?php
	// End of run details view
    }
	// Comment view (form)
    else if($_GET['view']=="comment"){
		$comment = fetch_comment($db, $_GET['run_id']);
?>
    Add a comment for run <?php echo $comment['number'];?>
    <form action="na62_runlist.php?view=submitcomment" method="POST">
        <input type="hidden" name="run_id" value="<?php echo $_GET['run_id']?>" >
        <textarea name="comment" cols=100 rows=10><?php echo $comment['usercomment']?></textarea><br>
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
$db->close();
?>
