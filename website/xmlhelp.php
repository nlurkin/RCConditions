<?php

function formatXML($string){
	$dom = new DOMDocument("");
	$dom->preserveWhiteSpace = FALSE;
	$dom->loadXML($string);
	$dom->formatOutput = TRUE;
	return $dom->saveXml($dom->documentElement);
}
?>

<html>
<head>
<title>NA62 run conditions xml export help</title>
<link rel="stylesheet" type="text/css" href="na62.css">
<script type="text/javascript" language="javascript">
function setHeight(id){
	document.getElementById(id).style.height = document.getElementById(id).scrollHeight + 5 + "px";
}
</script>
</head>
<body>
<h1>Description of the NA62 conditions XML</h1>
<a href="na62_runlist.php" class="back">Back</a>
<h2>Structure</h2>
The global structure of the XML file is the following:
<br>
<textarea rows=1 id="TA-main" class="XML" disabled>
<?php echo formatXML('<Run totalL0="57979" totalMerger="54410" id="1559" endTime="1419026461" startTime="1418639008" totalBurst="578"><Event Timestamp="1408721752"><xxx>/**lots of allowed "NA62 Config" XML tags that are described later**/</xxx></Event></Run>');
?>
</textarea>
<script>
setHeight("TA-main");
</script>
<br>
The top node &lt;Run&gt; encloses the whole document and contains attributes corresponding to some metadata about the Run itself:
<ul>
<li> id: run number
<li> startTime: start of run unix timestamp
<li> endTime: end of run unix timestamp
<li> totalBurst: number of bursts in the run
<li> totalL0: integrated number of L0 recorded by the RunControl. 
<li> totalMerger: integrated number of events sent to the merger. 
</ul>

The RunControl recording is event-based and this is reflected in the structure of the XML file with the &lt;Event&gt; tag. Its only attribute is:
<ul>
<li> Timestamp: unix timestamp of the event
</ul>
This &lt;Event&gt; tag can contains many different type of "NA62 Config" tags. For each of these tags, the RunControl always exports the event preceding the start of run and the event following the end of run in order to be certain to always have the full set of conditions that were applied for the full length of the run.

<h2>NA62 config tags</h2>
This section contains a list and description of all the tags, or tags blocks, that can be found within the &lt;Event&gt; tag.

<h4>&lt;TEL62&gt;</h4>
<textarea cols=1 rows=1 ID="TA-TEL62" class="XML" disabled>
<?php echo formatXML('<Event Timestamp="1408721752"><TEL62><TELL_CEDAR_2.Source>1</TELL_CEDAR_2.Source><TELL_LAV8.Source>1</TELL_LAV8.Source><TELL_LAV9.Source>1</TELL_LAV9.Source></TEL62></Event>');?>
</textarea>
<script>
setHeight("TA-TEL62");
</script>
<ul>
<li> TEL62Name.Source: 1 means that the TEL62 called "TEL62Name" in the RunControl is included in the Run. 0 means it is excluded.
</ul>
<h4>&lt;CREAM&gt;</h4>
<textarea cols=1 rows=1 ID="TA-CREAM" class="XML" disabled>
<?php echo formatXML('<Event Timestamp="1408721752"><CREAM><CREAMCrate2A><CrateNumber>4</CrateNumber><Producer>,4:3-4,4:9-10,4:13-20</Producer><TotalCreams>12</TotalCreams></CREAMCrate2A></CREAM></Event>');?>
</textarea>
<script>
setHeight("TA-CREAM");
</script>
<br />
The CREAM block describes the CREAM system. The system consists in a list of logical crates labeled nX where n=1..8 and X=A..D. Each crate contains several fields:
<ul>
<li> CrateNumber: Physical number of the crate
<li> Producer: List of slots containing a CREAM module producing data (21 slots/crate). The format is ",crateNumber:slots-range,crateNumber:slots-range..."
<li> TotalCreams: Total number of CREAM module for the crate.
</ul>
<h4>&lt;Board tags&gt;</h4>
<textarea cols=1 rows=1 ID="TA-board" class="XML" disabled>
<?php echo formatXML('<Event Timestamp="1408721752"><LTU_STRAW><SplitContent>"LTU specific XML"</SplitContent></LTU_STRAW><TELL_CHANTI_2><SplitStore></SplitStore></TELL_CHANTI_2></Event>');?>
</textarea>
<script>
setHeight("TA-board");
</script>
<br />
The tag itself is the name of the board in the RunControl. It contains the XML configuration of the board:
<ul>
<li> SplitContent: Contains the XML configuration file sent to the board.
<li> SplitStore: Contains the XML configuration file that has been reported by the board either after START_RUN or after END_RUN (depending on the board: TEL62=END_RUN, others=START_RUN)
</ul>
This information being too big to hold into a single oracle database text field, it is divided in chunks of max 4000 characters. The information given here in these two tags is the recombination of those chunks. It can happen on some files that the order of the chunks are messed up.

<h4>&lt;Detector tags&gt;</h4>
<textarea cols=1 rows=1 ID="TA-detector" class="XML" disabled>
<?php echo formatXML('<Event Timestamp="1408721752"><CEDAR><DefaultEnabled>TRUE</DefaultEnabled><Name>,0x4</Name><Enabled>TRUE</Enabled><Sources>4</Sources></CEDAR><CHANTI><DefaultEnabled>FALSE</DefaultEnabled></CHANTI><CHOD><DefaultEnabled>FALSE</DefaultEnabled></CHOD></Event>');?>
</textarea>
<script>
setHeight("TA-detector");
</script>
<br>
The tag itself is the name of the detector subsystem in the RunControl. It gives some information about the state of the detector in the RunControl:
<ul>
<li> DefaultEnabled: Is the detector included/excluded by default in the recipe?
<li> Name: Hexadecimal detector source ID (See TDAQ note).
<li> Enabled: Is the detector included/excluded?
<li> Sources: Number of data sources enabled (acquisition boards)
</ul>

<h4>&lt;RunInfo&gt;</h4>
<textarea cols=1 rows=1 ID="TA-runinfo" class="XML" disabled>
<?php echo formatXML('<Event Timestamp="1408721752"><RunInfo><RunNumber>1558</RunNumber><RunStartTime>2014.12.15 10:55:42.787</RunStartTime><StartRunComment>Calibration data</StartRunComment><ShiftCrew>SV &amp; RF</ShiftCrew><BeamType>x</BeamType><RunStopTime>2014.12.15 13:57:52.540</RunStopTime><EndRunComment>x</EndRunComment></RunInfo></Event>');?>
</textarea>
<script>
setHeight("TA-runinfo");
</script>
<br />
Gives information recorded by the RunManager at start and end of run:
<ul>
<li> RunNumber: Number of the run.
<li> RunStartTime: Start time of the run.
<li> StartRunComment: Comment given by the shifters at start of run.
<li> ShiftCrew: Shifters at the start of run.
<li> BeamType: Not provided currently.
<li> RunStopTime: End time of the run.
<li> EndRunComment: Comment given by the shifters at end of run.
</ul>

</body>
</html>
