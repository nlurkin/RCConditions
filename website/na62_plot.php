<?php // content="text/plain; charset=utf-8"
error_reporting ( E_ALL );
ini_set ( 'display_errors', TRUE );
ini_set ( 'display_startup_errors', TRUE );

require_once ('jpgraph/jpgraph.php');
require_once ('jpgraph/jpgraph_line.php');
require_once ('jpgraph/jpgraph_date.php');

include ("config.php");
include ("na62_helper.php");
include ("na62_fetch.php");

abstract class TVType{
	const WT10  = 0;
	const WXION = 1;
}

function doPlot($db, $tstart, $tstop, $which, $width){
	if( $which == TVType::WT10 )
		$tvArray = fetch_RunTV($db, $tstart, $tstop, "T10_intensity");
	elseif( $which == TVType::WXION)
		$tvArray = fetch_RunTV($db, $tstart, $tstop, "XION_intensity");

	$datay1 = array();
	$lArray = array();
	foreach ($tvArray as $line){
		array_push($datay1, $line["value"]);
		array_push($lArray, $line["timeval"]);
	}
	// Setup the graph
	$graph = new Graph($width,250);
	$graph->SetScale("datlin");

	$theme_class=new UniversalTheme;

	$graph->SetTheme($theme_class);
	$graph->img->SetAntiAliasing(false);
	if( $which == TVType::WT10 )
		$graph->title->Set('T10 Intensity during run [E11]');
	elseif( $which == TVType::WXION)
		$graph->title->Set('Argonion counts during run');
	$graph->SetBox(false);

	$graph->img->SetAntiAliasing();

	$graph->yaxis->HideLine(false);
	$graph->yaxis->HideTicks(false,false);

	$graph->xgrid->Show();
	$graph->xgrid->SetLineStyle("solid");
	$graph->xgrid->SetColor('#E3E3E3');

	$graph->xaxis->SetLabelAngle(45);

	// Create the first line
	$p1 = new LinePlot($datay1, $lArray);
	$p1->SetStepStyle();
	$graph->Add($p1);
	$p1->SetColor("#6495ED");
	//$p1->SetLegend('I [E11]');

	$graph->legend->SetFrameWeight(1);

	// Output line
	$graph->Stroke();
}

$db = new DBConnect ();

if (! $db->init ( $_na62dbHost, $_na62dbUser, $_na62dbPassword, $_na62dbName, $_na62dbPort )) {
	die ( "Connection failed: " . $db->getError () . "<br>" );
}

if($_GET["which"]=="T10")
	doPlot($db, $_GET["tstart"], $_GET["tstop"], TVType::WT10, 600);
else if($_GET["which"]=="XION")
	doPlot($db, $_GET["tstart"], $_GET["tstop"], TVType::WXION, 600);
?>

