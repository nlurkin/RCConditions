<?php

// Multi-line display
if(isset($_POST["displaymore"])){
	$moreInfo = $_POST["displaymore"]!="";
	setcookie("displaymore", true, time()+86400*365);
}
elseif (isset ( $_COOKIE ["displaymore"] ))
	$moreInfo = ( bool ) $_COOKIE ["displaymore"];
else
	$moreInfo = false;
