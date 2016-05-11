<?php
// Error handling
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

// Get site specific configuration
include ("config.php");
include ("na62_helper.php");
include ("na62_fetch.php");

// Define some global variables
$frequencyUnits = Array (
		"Hz",
		"kHz",
		"MHz" 
);
$db = new DBConnect ();
$dataArray = Array ();
$currentLast = 20;
$maxLoading = 10;

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}

include("na62_getglobals.php");

	// Get data from Database
if (! isset ( $_GET ['view'] ) || $_GET ['view'] == '' || $_GET ['view'] == 'csv') {
	//$dataArray = fetch_all ( $db , 0, $currentLast);
	$dataArray = Array();
} else if (isset ( $_GET ['view'] ) && $_GET ['view'] == "search") {
	$runLimits = 100;
	$rowOffset = 0;
	if (isset ( $_GET ['page'] ))
		$rowOffset = $_GET ['page'] * runLimits;
	$currentPage = $rowOffset / $runLimits;
	
	$searchParams = Array ();
	if (isset ( $_GET ["run_from"] ) && ! empty ( $_GET ["run_from"] ))
		$searchParams ["run_from"] = $_GET ["run_from"];
	if (isset ( $_GET ["run_to"] ) && ! empty ( $_GET ["run_to"] ))
		$searchParams ["run_to"] = $_GET ["run_to"];
	if (isset ( $_GET ["date_from"] ) && ! empty ( $_GET ["date_from"] ))
		$searchParams ["date_from"] = $_GET ["date_from"];
	if (isset ( $_GET ["date_to"] ) && ! empty ( $_GET ["date_to"] ))
		$searchParams ["date_to"] = $_GET ["date_to"];
	if (isset ( $_GET ["detectors_en"] ))
		$searchParams ["detectors_en"] = $_GET ["detectors_en"];
	if (isset ( $_GET ["triggers_en"] ))
		$searchParams ["triggers_en"] = $_GET ["triggers_en"];
	if (isset ( $_GET ["primitive"] ))
		$searchParams ["primitive"] = $_GET ["primitive"];
	$sqlwhere = generate_search_sql ( $db, $searchParams );
	$dataArray = fetch_search ( $db, $rowOffset, $runLimits, $sqlwhere );
	
	$nPages = ( int ) (fetch_nRuns ( $db, $sqlwhere ) / $runLimits) + 1;
}

// Display data
// CSV view
if (isset ( $_GET ['view'] ) && $_GET ['view'] == "csv") {
	header ( 'Content-disposition: attachment; filename=na62_runlist.csv' );
	header ( 'Content-type: text/plain' );
	
	if (count ( $dataArray ) > 0) {
		echo "Run #;Type;Start;End;Trigger(Downscaling);
				Start comment;Detectors;End comment\n";
		foreach ( $dataArray as $row ) {
			$triggerstring = trim ( $row ['triggerstring'], '+' );
			$enabledstring = $row ['enabledstring'];
			echo $row ['number'] . ";" . $row ['runtypename'] . ";" . $row ['timestart'] . ";" . $row ['timestop'] . ";" . $triggerstring . ";" . $row ['startcomment'] . ";" . $enabledstring . ";" . $row ['endcomment'] . "\n";
		}
	}
}  // Comment view (submit - no display)
else if (isset ( $_GET ['view'] ) && $_GET ['view'] == "submitcomment") {
	$run_id = $_POST ['run_id'];
	$comment = $_POST ['comment'];
	
	$sql = "UPDATE run SET run.usercomment=? WHERE run.id=?";
	if ($db->executeUpdate ( $sql, "si", $comment, $run_id )) {
		header ( "Location:na62_runlist.php?view=details&run_id=" . $run_id );
	}
	die ();
}  // Download XML view
else if (isset ( $_GET ['view'] ) && $_GET ['view'] == "downxml") {
	$dbres = fetch_xml ( $db, $_GET ['run_id'] );
	$file_name = $dbres ['number'] . $_na62XmlExtension;
	$file_url = $_na62XmlAddress . $file_name;
	header ( 'Content-type: ' . $_na62XmlMIMEType );
	header ( "Content-disposition: attachment; filename=\"" . $file_name . "\"" );
	readfile ( $file_url );
	exit ();
}  // Multi-run table views (normal and search)
else {
	?>
<!DOCTYPE html>
<html>
<head>
<title>NA62 Run Infos</title>
<link rel="stylesheet" type="text/css" href="na62.css">
<link rel="stylesheet" type="text/css" href="collapse.css">
<script src="https://code.jquery.com/jquery-1.11.2.min.js"></script>
<script src="https://code.jquery.com/ui/1.11.2/jquery-ui.min.js"></script>
<script type="text/javascript" src="drag_collapse.js"></script>
<script type="text/javascript">
currentLast = <?php echo $currentLast;?>;
max = <?php echo $maxLoading;?>;
loading = false;

<?php if(!isset($_GET['view']) || $_GET['view']!="search"){?>
jQuery(window).scroll(function(){
	if (jQuery(window).scrollTop() == jQuery(document).height() - jQuery(window).height() && loading==false){
		loading = true;
		$('#tbl_lst_runs > tbody > tr:last').after("<tr><td colspan='9' class='loading'><img alt='loader' src='ajax-loader.gif'>Loading more runs</td></tr>");
		$.ajax({
	        url : "na62_getdata.php?from=" + currentLast + "&max=" + max,
	        type : 'GET',
	        dataType : 'text',
	        success : function(data) {
	        	$('#tbl_lst_runs >tbody > tr:last').remove();
	        	$('#tbl_lst_runs > tbody > tr:last').after(data);
	        	currentLast += max;
	        	loading = false;
	        },
	        error : function() {
	            console.log('error');
	            loading = false;
	        }
	    });
		
	}
});
<?php }?>
function initWindow(){
	i=0;
	intervalID = setInterval(function(){
		if(loading) return;
		if(i>=currentLast) clearInterval(intervalID);
		$('#tbl_lst_runs > tbody > tr:last').after("<tr><td colspan='9' class='loading'><img alt='loader' src='ajax-loader.gif'>Loading more runs</td></tr>");
		loading = true
		$.ajax({
	        url : "na62_getdata.php?from=" + i + "&max=" + max,
	        type : 'GET',
	        dataType : 'text',
	        success : function(data) {
	        	$('#tbl_lst_runs >tbody > tr:last').remove();
	        	$('#tbl_lst_runs > tbody > tr:last').after(data);
	        	i += max;
	        	loading = false;
	        },
	        error : function() {
	            console.log('error');
	            loading = false;
	        }
	    });
	}, 500);
}
</script>
</head>
<body>
<?php
	if (! isset ( $_GET ['view'] ) || $_GET ['view'] == "" || $_GET ['view'] == "search") {
		?>
	<h1>NA62 Run Conditions Database</h1>
	<div style="text-align: center; max-width: 600px; margin: 0 auto;">
		This page displays the list of runs recorded by the RunControl. This
		is only an extract of all the information present in the RunControl
		database. This list can be <a href="na62_runlist.php?view=csv">Downloaded
			as CSV file</a>
	</div>
	<div style="width: 1100px">
		<ul>
			<li><b>The triggers are given with their downscaling (/ symbol) and
					the reference detector for the timing (in the parenthesis).</b>
			
			<li><b>Click on the "Details" link to see more details about the run
					(trigger and enabled detectors timeline and few other metadata).</b>
				<b>You can also add an offline comment to the run (good for x, bad
					for y, ...)</b>
			
			<li><b>The full set of values and events recorded by RunControl for
					the run (including board configuration) is available for download
					by clicking the "XML" link. The XML format is explained <a
					href="xmlhelp.php">here</a>.
			</b>
			
			<li><b>More details on the primitive triggers <a
					href="primitivehelp.php">here</a></b>
		
		</ul>
	</div>
	<div class="search-form">
		<h4>Search</h4>
<?php
		if (isset ( $_GET ["run_from"] ))
			$run_from = $_GET ["run_from"];
		else
			$run_from = "";
		if (isset ( $_GET ["run_to"] ))
			$run_to = $_GET ["run_to"];
		else
			$run_to = "";
		if (isset ( $_GET ["date_from"] ))
			$date_from = $_GET ["date_from"];
		else
			$date_from = "";
		if (isset ( $_GET ["date_to"] ))
			$date_to = $_GET ["date_to"];
		else
			$date_to = "";
		
		$det_checked = array (
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
		if (isset ( $_GET ["detectors_en"] )) {
			foreach ( $_GET ["detectors_en"] as $det )
				$det_checked [$det] = "checked";
		}
		
		$trigger_checked = array (
				"calibration" => "",
				"sync" => "",
				"periodic" => "" 
		);
		if (isset ( $_GET ["triggers_en"] )) {
			foreach ( $_GET ["triggers_en"] as $trigg )
				$trigger_checked [$trigg] = "checked";
		}
		if (isset ( $_GET ["nPrimComb"] ))
			$nPrimComb = $_GET ["nPrimComb"];
		else
			$nPrimComb = 0;
		if (isset ( $_GET ["primitive"] ))
			$selectedPrimitive = $_GET ["primitive"];
		else
			$selectedPrimitive = "";
		
		if (isset ( $_GET ['view'] ) && $_GET ['view'] == "search") {
			?>

	<div class="collapsep">&#x25C0</div>
		<div class="collapsem">&#9660</div>
		<div class="search-form-content">
<?php
		} else {
			?>
	<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="search-form-content" style="display: none;">
<?php
		}
		// Prepare primitive triggers array
		$primTypes = fetch_PrimitivesTypes ( $db );
		echo "<script>";
		echo "var triggers = [";
		$triggCombs = array ();
		foreach ( $primTypes as $type ) {
			array_push ( $triggCombs, "\"" . implode ( ",", $type ) . "\"" );
		}
		echo implode ( ",\n", $triggCombs );
		echo "];\n";
		echo "var primSelected = '" . $selectedPrimitive . "';\n";
		echo "</script>";
		?>
	<script>
	function applyTriggersList(){
		var nTriggers = document.getElementById("nPrimComb").value;
		var prim = document.getElementById("primitive");
		while(prim.options.length > 0) prim.remove(0);
		if(nTriggers>0){
			var els = triggers[nTriggers-1].split(",");
			for(var i =0; i< els.length; i++){
				var opt = document.createElement("option");
				opt.value = els[i];
				opt.innerHTML = els[i];
				prim.appendChild(opt);
			}
			if(nTriggers==<?php echo $nPrimComb; ?>) prim.value = primSelected;
			else prim.selectedIndex = 0;
		}
	}
	</script>
				<form action="na62_runlist.php" method="GET">
					<input type="hidden" name="view" value="search">
					<div class="leftsearch">
						<label class="main" for="run_from"><span>Run number</span></label>
						<input type="number" class="input-field" name="run_from"
							id="run_from" placeholder="From run #"
							value="<?php echo $run_from;?>"> <input type="number"
							class="input-field" name="run_to" id="run_to"
							placeholder="To run #" value="<?php echo $run_to;?>"> <label
							class="main" for="date_from"><span>Date </span></label> <input
							type="text" class="input-field-date" name="date_from"
							id="date_from" onfocus="(this.type='date')"
							onblur="(this.type='text')" placeholder="From date"
							value="<?php echo $date_from;?>"> <input type="text"
							class="input-field-date" name="date_to" id="date_to"
							onfocus="(this.type='date')" onblur="(this.type='text')"
							placeholder="To date" value="<?php echo $date_to;?>"> <label
							class="main" for="detectors_en[]"><span>Enabled detectors</span></label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[0]" value="CHANTI"
							<?php echo $det_checked["CHANTI"]; ?>> <label
							for="detectors_en[0]">CHANTI</label> <input type="checkbox"
							class="input-field-box" name="detectors_en[]"
							id="detectors_en[1]" value="CHOD"
							<?php echo $det_checked["CHOD"]; ?>> <label for="detectors_en[1]">CHOD</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[2]" value="GTK"
							<?php echo $det_checked["GTK"]; ?>> <label for="detectors_en[2]">GTK</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[3]" value="IRC_SAC"
							<?php echo $det_checked["IRC_SAC"]; ?>> <label
							for="detectors_en[3]">IRC_SAC</label> <input type="checkbox"
							class="input-field-box" name="detectors_en[]"
							id="detectors_en[4]" value="KTAG"
							<?php echo $det_checked["KTAG"]; ?>> <label for="detectors_en[4]">KTAG</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[5]" value="L0TP"
							<?php echo $det_checked["L0TP"]; ?>> <label for="detectors_en[5]">L0TP</label>
						<br> <label class="main"><span></span></label> <input
							type="checkbox" class="input-field-box" name="detectors_en[]"
							id="detectors_en[6]" value="LAV"
							<?php echo $det_checked["LAV"]; ?>> <label for="detectors_en[6]">LAV</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[7]" value="LKR"
							<?php echo $det_checked["LKR"]; ?>> <label for="detectors_en[7]">LKr</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[8]" value="MUV1"
							<?php echo $det_checked["MUV1"]; ?>> <label for="detectors_en[8]">MUV1&2
						</label> <input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[9]" value="MUV3"
							<?php echo $det_checked["MUV3"]; ?>> <label for="detectors_en[9]">MUV3</label>
						<input type="checkbox" class="input-field-box"
							name="detectors_en[]" id="detectors_en[10]" value="RICH"
							<?php echo $det_checked["RICH"]; ?>> <label
							for="detectors_en[10]">RICH</label> <input type="checkbox"
							class="input-field-box" name="detectors_en[]"
							id="detectors_en[11]" value="STRAW"
							<?php echo $det_checked["STRAW"]; ?>> <label
							for="detectors_en[11]">Straw</label>
					</div>
					<div class="rightSearch">
						<label class="main" for="run_from"><span>Triggers</span></label> <input
							type="checkbox" class="input-field-box" name="triggers_en[]"
							id="triggers_en[0]" value="calibration"
							<?php echo $trigger_checked["calibration"]; ?>> <label
							for="triggers_en[0]">Calib</label> <input type="checkbox"
							class="input-field-box" name="triggers_en[]" id="triggers_en[1]"
							value="sync" <?php echo $trigger_checked["sync"]; ?>> <label
							for="triggers_en[1]">Sync</label> <input type="checkbox"
							class="input-field-box" name="triggers_en[]" id="triggers_en[2]"
							value="periodic" <?php echo $trigger_checked["periodic"]; ?>> <label
							for="triggers_en[2]">Periodic</label> <label class="main"
							for="nPrimComb"><span>Primitives</span></label> <input
							type="range" min="0" max="7" name="nPrimComb" id="nPrimComb"
							placeholder="# Combination"
							value="<?php echo abs($nPrimComb); ?>"
							onChange="applyTriggersList();" onInput="applyTriggersList();"> <br>
						<br> <label class="main" for="primitive"><span></span></label> <select
							id="primitive" name="primitive" class="input-field"
							style="width: 300px">
						</select>
						<div class="form-submit">
							<input type="submit" value="Search"> <input type="button"
								value="Reset" onclick="location.href='na62_runlist.php';">
						</div>
					</div>
				</form>
			</div>
		</div>
	</div>
	<script>
	applyTriggersList();
	</script>
	<br>
	<?php
		$searchLine = "";
		if (sizeof ( $_GET ) > 0)
			$searchLine = "?" . implode ( "&", array_map ( function ($v, $k) {
				$retArray = array();
				if(is_array($v)){
					foreach($v as $vvalue) array_push($retArray, $k . "[]=" . $vvalue);
				}
				else array_push($retArray, $k . "=" . $v);
				return implode("&", $retArray);
			}, $_GET, array_keys ( $_GET ) ) );
		
		if ($moreInfo)
			$moreInfoChecked = "checked";
		else
			$moreInfoChecked = "";
		?>
	<div style="text-align: left; float: left;">
		<form action="na62_runlist.php<?php echo $searchLine;?>" method="POST"
			style="margin: 0; padding-bottom: 10px;">
			<input type="hidden" name="displaymoreset" value="true"> <label
				for="displaymore" class="main"><span>&nbsp;</span></label> <input
				type="checkbox" class="input-field-box" name="displaymore"
				id="displaymore" value="more" onChange="this.form.submit()"
				<?php echo $moreInfoChecked;?>> <label for="displaymore"
				style="width: 200px; font: 11px Verdana, Arial, Helvetica, sans-serif;">Multi-line
				run display</label>
		</form>
	</div>
<?php
		if (isset ( $_GET ['view'] ) && $_GET ['view'] == "search") {
			?>
	<div style="text-align: right; float: right; bottom: 0;">
	Page:
	<?php if($rowOffset>0) {?><a
			href="na62_runlist.php?view=search&page=<?php echo $currentPage-1;?>">Prev</a><?php } ?>
<?php

			for($i = 0; $i < $currentPage + 5 && $i < $nPages; $i ++) {
				if ($i == $currentPage)
					echo ($i + 1) . " ";
				else
					echo '<a href="na62_runlist.php?view=search&page="' . $i . '">' . ($i + 1) . '</a> ';
			}
			?>
	<a
			href="na62_runlist.php?view=search&rowoffset=<?php echo $currentPage+1;?>">Next</a>
	</div>

<?php
		} else {
			echo "<br>";
		}
		if ($moreInfo) {
			$rowspan = 2;
			$colspan = 2;
			$commentSize = "500px";
		} else {
			$rowspan = 1;
			$colspan = 1;
			$commentSize = "300px";
		}
		?>
    <table border=1 style="table-layout: fixed;" id="tbl_lst_runs" class="big">
		<tr>
			<th width='50px'>Run #</th>
			<th width='120px'>Type</th>
			<th width='150px'>Start</th>
			<th width='150px'>End</th>
			<?php
		if (! $moreInfo) {
			?>
			<th width='200px'>Detectors</th>
			<?php
		}
		?>
			<th width='<?php echo $commentSize;?>' colspan=<?php echo $colspan;?>>Start
				run comment</th>
			<th width='*' style='text-align: right'
				rowspan=<?php echo $rowspan;?>>Trigger/Downscaling(Ref)</th>
			<th width='50px' rowspan=<?php echo $rowspan;?>></th>
			<th width='50px' rowspan=<?php echo $rowspan;?>></th>
		</tr>
		<?php
		if ($moreInfo) {
			?>
		<tr>
			<th colspan=1>T10 (E11)</th>
			<th># bursts</th>
			<th># L0</th>
			<th>Detectors</th>
			<th colspan=2>End comment</th>
		</tr>
		<!-- <tr>
			<th colspan=5></th>
			<th>Offline comment</th>
		</tr>-->
<?php
		}
		if (count ( $dataArray ) > 0) {
			$i = 0;
			$css = Array (
					"r1",
					"r2" 
			);
			foreach ( $dataArray as $row ) {
				if (! isset ( $_GET ['view'] ) || $_GET ['view'] == "") {
					$triggerstring = prepare_trigger ( "search", $row );
					$enabledstring = prepare_enabled ( "all", $row );
				} else if ($_GET ['view'] == "search") {
					$enabledstring = prepare_enabled ( "search", $row );
					$triggerstring = prepare_trigger ( "search", $row );
				}
				echo "<tr class='d0 " . $css [$i % 2] . "' id='" . $row ['id'] . "'>";
				echo "<td>" . $row ['number'] . "</td><td>" . $row ['runtypename'] . "</td>";
				echo "<td>" . $row ['timestart'] . "</td><td>" . $row ['timestop'] . "</td>";
				if (! $moreInfo)
					echo "<td class='wrappable'>" . $enabledstring . "</td>";
				echo "<td style='text-align:right' class='wrappable' colspan=" . $colspan . ">" . $row ['startcomment'] . "</td>";
				echo "<td style='text-align:right' class='wrappable' rowspan=" . $rowspan . ">" . $triggerstring . "</td>";
				echo "<td rowspan=" . $rowspan . "><a href='na62_runlist.php?view=details&run_id=" . $row ['id'] . "'>Details</a></td>";
				
				$file_name = $row ['number'] . $_na62XmlExtension;
				$file_url = $_na62XmlAddress . $file_name;
				if (exists ( $file_url )) {
					echo "<td rowspan=" . $rowspan . "><a href='na62_runlist.php?view=downxml&run_id=" . $row ['id'] . "'>XML</a></td>";
				} else {
					echo "<td rowspan=" . $rowspan . "></td>";
				}
				echo "</tr>\n";
				if ($moreInfo) {
					echo "<tr class='d0 " . $css [$i % 2] . "'>";
					echo "<td colspan=1>" . $row["T10Max"] . "</td>";
					echo "<td>" . $row ["totalburst"] . "</td>";
					echo "<td>" . $row ["totalL0"] . "</td>";
					echo "<td class='wrappable'>" . $enabledstring . "</td>";
					echo "<td style='text-align:right' colspan=2>" . $row ["endcomment"] . "</td>";
					echo "</tr>\n";
				}
				$i ++;
			}
		}
		?>
    </table>
    <?php if((!isset($_GET['view']) || $_GET['view']!='search') && sizeof($dataArray)==0){?>
    <script type="text/javascript">
		initWindow();
    </script>
    <?php }?>
<?php
		// End of table views
	}  // Run details view
else if ($_GET ['view'] == "details") {
		// Get data from DB
		$runDetails = fetch_run_details ( $db, $_GET ['run_id'] );
		?>
	<h1>Details for Run# <?php echo $runDetails['number']?></h1>
	<div class="back">
	<a href="na62_runlist.php#<?php
		
		echo $_GET ['run_id']?>"
		>Back</a>
	<a href="na62_runlist.php?view=details&run_id=<?php
		
		echo $_GET ['run_id']-1?>"
		>Previous</a>
	<a href="na62_runlist.php?view=details&run_id=<?php
		
		echo $_GET ['run_id']+1?>"
		>Next</a>
	</div>
	<br>
	<div class="subtitle">Click on the arrow on the right of a box to
		collapse/expand it.</div>
	<div class="column" id="col1">
		<div class="dragbox" id="boxShifter">
			<h2>Shifter information</h2>
			<div class="collapsep">&#x25C0</div>
			<div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<td>Run Type</td>
						<td><?php echo $runDetails['runtypename'];?></td>
					</tr>
					<tr>
						<td>Start Time</td>
						<td><?php echo $runDetails['timestart'];?></td>
					</tr>
					<tr>
						<td>End Time</td>
						<td><?php echo $runDetails['timestop'];?></td>
					</tr>
					<tr>
						<td>Start Run comment</td>
						<td><?php echo $runDetails['startcomment'];?></td>
					</tr>
					<tr>
						<td>End Run comment</td>
						<td><?php echo $runDetails['endcomment'];?></td>
					</tr>
					<tr>
						<td>Offline comment <br> <a
							href="na62_runlist.php?view=comment&run_id=<?php echo $runDetails['id'];?>">Edit</a></td>
						<td><?php echo $runDetails['usercomment'];?></td>
					</tr>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>
				Periodic Trigger
				<p>*EOR=End Of Run</p>
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<th width="150px">Frequency</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
		foreach ( $runDetails ["periodic"] as $periodic ) {
			if ($periodic ["validityend"] == "")
				$end = "EOR";
			else
				$end = $periodic ["validityend"];
			$period = $periodic ["frequency"] * 1000000.;
			echo "<tr><td>" . humanReadable ( $period, $frequencyUnits ) . "</td><td>" . $periodic ["validitystart"] . "</td><td>" . $end . "</td></tr>";
		}
		?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>
				Calibration Trigger
				<p>*EOR=End Of Run</p>
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
		foreach ( $runDetails ["calibration"] as $calib ) {
			if ($calib ["validityend"] == "")
				$end = "EOR";
			else
				$end = $calib ["validityend"];
			echo "<tr><td>" . $calib ["validitystart"] . "</td><td>" . $end . "</td></tr>";
		}
		?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>
				NIM Trigger
				<p>*EOR=End Of Run</p>
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<th width="50px">Mask</th>
						<th width="200px">Trigger</th>
						<th width="50px">Downs.</th>
						<th width="55px">Ref. Det.</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
		foreach ( $runDetails ["nim"] as $nim ) {
			if ($nim ["validityend"] == "")
				$end = "EOR";
			else
				$end = $nim ["validityend"];
			$string = "";
			for($i = 0; $i <= 4; $i ++) {
				if ($string == "")
					$string = $nim ["det_" . $i];
				elseif ($nim ["det_" . $i] != "")
					$string = $string . "*" . $nim ["det_" . $i];
			}
			echo "<tr><td>" . $nim ["mask"] . "</td><td>" . $string . "</td>";
			echo "<td>" . $nim ["triggernimdownscaling"] . "</td>";
			echo "<td>" . $nim ["triggernimreference"] . "</td>";
			echo "<td>" . $nim ["validitystart"] . "</td><td>" . $end . "</td></tr>";
		}
		?>
				</table>
			</div>
		</div>
		<div class="dragbox">
			<h2>
				Primitive Trigger
				<p>*EOR=End Of Run</p>
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<th width="60px">Mask #</th>
						<th width="120px">Trigger</th>
						<th width="60px">Downs.</th>
						<th width="60px">Ref. Det.</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
		foreach ( $runDetails ["primitive"] as $prim ) {
			if ($prim ["validityend"] == "")
				$end = "EOR";
			else
				$end = $prim ["validityend"];
			$primNameArr = Array ();
			na62_primToNameAll($db, $prim);
			if (! is_null ( $prim ["maskA"] ))
				array_push ( $primNameArr, $prim ["maskA"] );
			if (! is_null ( $prim ["maskB"] ))
				array_push ( $primNameArr, $prim ["maskB"] );
			if (! is_null ( $prim ["maskC"] ))
				array_push ( $primNameArr, $prim ["maskC"] );
			if (! is_null ( $prim ["maskD"] ))
				array_push ( $primNameArr, $prim ["maskD"] );
			if (! is_null ( $prim ["maskE"] ))
				array_push ( $primNameArr, $prim ["maskE"] );
			if (! is_null ( $prim ["maskF"] ))
				array_push ( $primNameArr, $prim ["maskF"] );
			if (! is_null ( $prim ["maskG"] ))
				array_push ( $primNameArr, $prim ["maskG"] );
			echo "<tr><td>" . $prim ["masknumber"] . "</td><td>" . implode ( "x", $primNameArr ) . "</td><td>" . $prim ["triggerprimitivedownscaling"] . "</td><td>" . $prim ["triggerprimitivereference"] . "</td><td>" . $prim ["validitystart"] . "</td><td>" . $end . "</td></tr>";
		}
		?>
				</table>
			</div>
		</div>
	</div>
	<div class="column" id="col2">
		<div class="dragbox" id="boxCollected">
			<h2>Collected information</h2>
			<div class="collapsep">&#x25C0</div>
			<div class="collapsem">&#9660</div>
			<div class="dragbox-content">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<td>Run Number</td>
						<td><?php echo $runDetails['number']?></td>
					</tr>
					<tr>
						<td>Number of Bursts</td>
						<td><?php echo $runDetails['totalburst']?></td>
					</tr>
					<tr>
						<td>Number of L0</td>
						<td><?php echo $runDetails['totalL0']?></td>
					</tr>
					<tr>
						<td>Average L0/Burst</td>
						<td><?php 
						if($runDetails['totalburst']!=0) echo (int)($runDetails['totalL0']/$runDetails['totalburst'])?></td>
					</tr>
					<tr>
						<td>Average L0 rate</td>
						<td><?php 
						if($runDetails['totalburst']!=0) echo humanReadable ( $runDetails['totalL0']/$runDetails['totalburst']/3.3, $frequencyUnits, 2) ?></td>
					</tr>
					<tr>
						<td>Number of L1</td>
						<td><?php echo $runDetails['totalL1']?></td>
					</tr>
					<tr>
						<td>Number of L2</td>
						<td><?php echo $runDetails['totalL2']?></td>
					</tr>
				</table>
			</div>
		</div>
		<div class="dragbox" id="boxT10Intensity">
			<h2>
				T10 Intensity
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<img src="na62_plot.php?tstart=<?php echo $runDetails["timestart"]; ?>&tstop=<?php echo $runDetails["timestop"]; ?>" />
			</div>
		</div>
		<div class="dragbox" id="boxDetector">
			<h2>
				Enabled Detectors
				<p>*EOR=End Of Run</p>
			</h2>
			<div class="collapsep" style="display: inline;">&#x25C0</div>
			<div class="collapsem" style="display: none;">&#9660</div>
			<div class="dragbox-content" style="display: none;">
				<table style="table-layout: fixed; width: 100%"
					class="autoalternate">
					<tr>
						<th width="100px">Detector</th>
						<th width="80px">Source ID</th>
						<th width="*">From</th>
						<th width="*">Until*</th>
					</tr>
				<?php
		foreach ( $runDetails ["enableddetectors"] as $enabled ) {
			if ($enabled ["validityend"] == "")
				$end = "EOR";
			else
				$end = $enabled ["validityend"];
			echo "<tr><td>" . $enabled ["detectorname"] . "</td><td>" . $enabled ["detectorid"] . "</td><td>" . $enabled ["validitystart"] . "</td><td>" . $end . "</td></tr>";
		}
		?>
				</table>
			</div>
		</div>
		<div>
<?php
		// End of run details view
	}  // Comment view (form)
else if ($_GET ['view'] == "comment") {
		$comment = fetch_comment ( $db, $_GET ['run_id'] );
		?>
    Add a comment for run <?php echo $comment['number'];?>
    <form action="na62_runlist.php?view=submitcomment" method="POST">
				<input type="hidden" name="run_id"
					value="<?php echo $_GET['run_id']?>">
				<textarea name="comment" cols=100 rows=10><?php echo $comment['usercomment']?></textarea>
				<br> <input type="submit" value="submit">
			</form>
<?php
		// End of comment view
	}
	?>
</body>
</html>
<?php
	// End of display views
}

// Close connection to DB
$db->close ();
?>
