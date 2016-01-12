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

function doT10Plot($db, $tstart, $tstop, $width){
	$t10Array = fetch_RunT10($db, $tstart, $tstop);

	$datay1 = array();
	$lArray = array();
	foreach ($t10Array as $line){
		array_push($datay1, $line["value"]);
		array_push($lArray, $line["time"]);
	}
	// Setup the graph
	$graph = new Graph($width,250);
	$graph->SetScale("datlin");

	$theme_class=new UniversalTheme;

	$graph->SetTheme($theme_class);
	$graph->img->SetAntiAliasing(false);
	$graph->title->Set('T10 Intensity during run [E11]');
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

doT10Plot($db, $_GET["tstart"], $_GET["tstop"], 600);
?>

