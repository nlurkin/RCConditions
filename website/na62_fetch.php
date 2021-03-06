<?php
function fetch_all($db) {
	// Get all data from DB using full views
	$sql = "SELECT run.id, run.number, run.startcomment, runtype.runtypename,
		run.timestart, run.timestop, viewtriggerfull.triggerstring,
        viewenableddet.enabledstring, run.endcomment, run.totalburst, run.totalL0
        FROM run
        LEFT JOIN runtype ON (runtype.id = run.runtype_id)
        LEFT JOIN viewenableddet ON (viewenableddet.run_id = run.id)
        LEFT JOIN viewtriggerfull ON (run.id = viewtriggerfull.run_id)
        GROUP BY run.id
        ORDER BY run.number DESC";
	if ($db->executeGet ( $sql ) > 0) {
		// Fill the array with data
		$jsonArray = Array ();
		while ( $row = $db->next () ) {
			array_push ( $jsonArray, $row );
		}
		return $jsonArray;
	} else {
		die ( "No data in database" );
	}
}
function fetch_nRuns($db, $sqlwhere) {
	$sql = "SELECT run.id FROM run JOIN runtype";
	if (! empty ( $sqlwhere ))
		$sql = $sql . " " . $sqlwhere . " AND ";
	else
		$sql = $sql . " ON ";
	$sql = $sql . " runtype.id = run.runtype_id GROUP BY run.id";
	$nrun = $db->executeGet ( $sql );
	return $nrun;
}
function fetch_enabled($db, $runID, $tsStart, $tsStop) {
	$sql = "SELECT DISTINCT enableddetectors.detectorname
		FROM enableddetectors
		WHERE enableddetectors.run_id = " . $runID . "
		AND (enableddetectors.validityend > '" . $tsStart . "'
		OR enableddetectors.validityend is NULL)";
	if (! empty ( $tsStop ))
		$sql = $sql . " AND enableddetectors.validitystart < '" . $tsStop . "'";
	$sql = $sql . "ORDER BY enableddetectors.detectorname";
	$db->executeGet ( $sql );
	
	$enabledArray = Array ();
	while ( $row = $db->next () ) {
		array_push ( $enabledArray, $row ["detectorname"] );
	}
	return $enabledArray;
}
function fetch_periodic($db, $runID, $tsStart, $tsStop) {
	global $frequencyUnits;
	
	$sql = "SELECT viewperiodic.frequency
		FROM viewperiodic
		WHERE viewperiodic.run_id = " . $runID . "
		AND (viewperiodic.validityend > '" . $tsStart . "'
		OR viewperiodic.validityend is NULL)";
	if (! empty ( $tsStop ))
		$sql = $sql . " AND viewperiodic.validitystart < '" . $tsStop . "'";
	$db->executeGet ( $sql );
	
	$periodicArray = Array ();
	while ( $row = $db->next () ) {
		array_push ( $periodicArray, humanReadable ( $row ["frequency"] * 1000000., $frequencyUnits ) );
	}
	return $periodicArray;
}
function fetch_calib($db, $runID, $tsStart, $tsStop) {
	$sql = "SELECT viewcalibration.id
		FROM viewcalibration
		WHERE viewcalibration.run_id = " . $runID . "
		AND (viewcalibration.validityend > '" . $tsStart . "'
		OR viewcalibration.validityend is NULL)";
	if (! empty ( $tsStop ))
		$sql = $sql . " AND viewcalibration.validitystart < '" . $tsStop . "'";
	
	if ($db->executeGet ( $sql ) > 0)
		return True;
	else
		return False;
}
function fetch_sync($db, $runID, $tsStart, $tsStop) {
	$sql = "SELECT viewsync.id
		FROM viewsync
		WHERE viewsync.run_id = " . $runID . "
		AND (viewsync.validityend > '" . $tsStart . "'
		OR viewsync.validityend is NULL)";
	if (! empty ( $tsStop ))
		$sql = $sql . " AND viewsync.validitystart < '" . $tsStop . "'";
	
	if ($db->executeGet ( $sql ) > 0)
		return True;
	else
		return False;
}
function fetch_nim($db, $runID, $tsStart, $tsStop) {
	$sql = "SELECT DISTINCT viewnimname.triggernimdownscaling, viewnimname.triggernimreference, viewnimname.det_0,
		viewnimname.det_1, viewnimname.det_2, viewnimname.det_3, viewnimname.det_4
		FROM viewnimname
		WHERE viewnimname.run_id = " . $runID . "
		AND (viewnimname.validityend > '" . $tsStart . "'
		OR viewnimname.validityend is NULL)";
	if (! empty ( $tsStop ))
		$sql = $sql . " AND viewnimname.validitystart < '" . $tsStop . "'";
	$db->executeGet ( $sql );
	
	$NIMArray = Array ();
	while ( $row = $db->next () ) {
		array_push ( $NIMArray, $row );
	}
	return $NIMArray;
}
function fetch_primitives($db, $runID, $tsStart, $tsStop) {
	$sql = "SELECT DISTINCT viewprimitivename.triggerprimitivedownscaling, viewprimitivename.triggerprimitivereference, viewprimitivename.maskA,
		viewprimitivename.maskB, viewprimitivename.maskC, viewprimitivename.maskD, viewprimitivename.maskE, viewprimitivename.maskF,
		viewprimitivename.maskG
		FROM viewprimitivename
		WHERE viewprimitivename.run_id = " . $runID . "
		AND (viewprimitivename.validityend > '" . $tsStart . "'
		OR viewprimitivename.validityend is NULL)";
	
	if (! empty ( $tsStop ))
		$sql = $sql . " AND viewprimitivename.validitystart < '" . $tsStop . "'";
	$db->executeGet ( $sql );
	
	$PrimArray = Array ();
	while ( $row = $db->next () ) {
		array_push ( $PrimArray, $row );
	}
	return $PrimArray;
}
function generate_search_sql($searchParams) {
	// Get and verify search parameters
	$whereArray = Array ();
	$joinArray = Array ();
	if (isset ( $searchParams ["run_from"] )) {
		if (is_numeric ( $searchParams ["run_from"] ))
			array_push ( $whereArray, "run.number >= " . $searchParams ["run_from"] );
	}
	if (isset ( $searchParams ["run_to"] )) {
		if (is_numeric ( $searchParams ["run_to"] ))
			array_push ( $whereArray, "run.number <= " . $searchParams ["run_to"] );
	}
	if (isset ( $searchParams ["date_from"] )) {
		if (strtotime ( $searchParams ["date_from"] ) !== false)
			array_push ( $whereArray, "run.timestart >= " . $searchParams ["date_from"] );
	}
	if (isset ( $searchParams ["date_to"] )) {
		if (strtotime ( $searchParams ["date_to"] ) !== false)
			array_push ( $whereArray, "run.timestart <= " . $searchParams ["date_to"] );
	}
	if (isset ( $searchParams ["detectors_en"] )) {
		foreach ( $searchParams ["detectors_en"] as $key => $det ) {
			array_push ( $joinArray, "enableddetectors as d" . $key );
			array_push ( $whereArray, "d" . $key . ".run_id = run.id AND d" . $key . ".detectorname = \"" . $det . "\"" );
		}
	}
	
	if (isset ( $searchParams ["triggers_en"] )) {
		foreach ( $searchParams ["triggers_en"] as $key => $trigg ) {
			array_push ( $joinArray, "view" . $trigg );
			array_push ( $whereArray, "view" . $trigg . ".run_id = run.id" );
		}
	}
	if (isset ( $searchParams ["primitive"] )) {
		array_push ( $joinArray, "viewprimitive" );
		array_push ( $whereArray, "viewprimitive.run_id = run.id AND viewprimitive.triggerstring LIKE '" . $searchParams ["primitive"] . "/%'" );
	}
	
	$sql = "";
	if (sizeof ( $joinArray ) > 0)
		$sql = $sql . " JOIN " . implode ( " JOIN ", $joinArray );
	if (sizeof ( $whereArray ) > 0)
		$sql = $sql . " ON " . implode ( " AND ", $whereArray );
	
	return $sql;
}
function fetch_search($db, $offset, $limits, $sqlwhere) {
	// Get data from DB
	$sql = "SELECT run.id, run.number, run.startcomment, runtype.runtypename, run.timestart,
			run.timestop, run.endcomment, run.totalburst, run.totalL0
        FROM run
        JOIN runtype";
	if (! empty ( $sqlwhere ))
		$sql = $sql . " " . $sqlwhere . " AND ";
	else
		$sql = $sql . " ON ";
	$sql = $sql . " runtype.id = run.runtype_id GROUP BY run.id
        ORDER BY run.number DESC LIMIT " . $limits . " OFFSET " . $offset;
	
	// Fill the array with data
	$jsonArray = Array ();
	if ($db->executeGet ( $sql ) > 0) {
		while ( $row = $db->next () ) {
			array_push ( $jsonArray, $row );
		}
		
		foreach ( $jsonArray as $key => $value ) {
			// Fetch enabled detectors
			$jsonArray [$key] ["enableddetectors"] = fetch_enabled ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
			
			// Fetch periodic triggers
			$jsonArray [$key] ["periodic"] = fetch_periodic ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
			
			// Fetch calibration
			$jsonArray [$key] ["calibration"] = fetch_calib ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
			
			// Fetch synchronisation
			$jsonArray [$key] ["sync"] = fetch_sync ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
			
			// Fetch NIM triggers
			$jsonArray [$key] ["NIM"] = fetch_nim ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
			
			// Fetch Primitive triggers
			$jsonArray [$key] ["Primitive"] = fetch_primitives ( $db, $value ["id"], $value ["timestart"], $value ["timestop"] );
		}
	}
	/*
	 * else{
	 * die("No data in database");
	 * }
	 */
	return $jsonArray;
}
function fetch_run_details($db, $runID) {
	$sql = "SELECT run.id, run.number, runtype.runtypename, run.timestart, run.timestop,
		run.startcomment, run.endcomment, run.totalburst, run.totalL0, run.usercomment,
		 run.totalL1, run.totalL2
		FROM run
		LEFT JOIN runtype ON (runtype.id = run.runtype_id)
		where run.id=" . $runID;
	
	// Fill the array with data
	if ($db->executeGet ( $sql ) > 0) {
		$mainrow = $db->next ();
		
		$sql = "SELECT DISTINCT viewperiodic.validitystart, viewperiodic.validityend, viewperiodic.frequency
						FROM viewperiodic WHERE run_id=" . $runID . " ORDER BY validitystart";
		// Fill the array with data
		$mainrow ["periodic"] = Array ();
		if ($db->executeGet ( $sql ) > 0) {
			while ( $row = $db->next () ) {
				array_push ( $mainrow ["periodic"], $row );
			}
		}
		
		$sql = "SELECT viewcalibration.validitystart, viewcalibration.validityend
			FROM viewcalibration WHERE run_id=" . $runID . " ORDER BY validitystart";
		// Fill the array with data
		$mainrow ["calibration"] = Array ();
		if ($db->executeGet ( $sql ) > 0) {
			while ( $row = $db->next () ) {
				array_push ( $mainrow ["calibration"], $row );
			}
		}
		
		$sql = "SELECT DISTINCT viewnimtype.validitystart, viewnimtype.validityend, viewnimtype.mask,
			viewnimtype.triggernimdownscaling, viewnimtype.triggernimreference,
			viewnimname.det_0, viewnimname.det_1, viewnimname.det_2, viewnimname.det_3, viewnimname.det_4
			FROM viewnimtype
			LEFT JOIN viewnimname ON (viewnimtype.nim_id = viewnimname.nim_id)
			WHERE viewnimtype.run_id=" . $runID . " ORDER BY validitystart";
		// Fill the array with data
		$mainrow ["nim"] = Array ();
		if ($db->executeGet ( $sql ) > 0) {
			while ( $row = $db->next () ) {
				array_push ( $mainrow ["nim"], $row );
			}
		}
		
		$sql = "SELECT DISTINCT viewprimitivename.validitystart,
			viewprimitivename.validityend, viewprimitivename.maskA,
			viewprimitivename.maskB, viewprimitivename.maskC,
			viewprimitivename.maskD, viewprimitivename.maskE,
			viewprimitivename.maskF, viewprimitivename.maskG,
			viewprimitivename.triggerprimitivedownscaling,
			viewprimitivename.triggerprimitivereference,
			viewprimitivename.masknumber
			FROM viewprimitivename
			WHERE viewprimitivename.run_id=" . $runID . " ORDER BY validitystart";
		// Fill the array with data
		$mainrow ["primitive"] = Array ();
		if ($db->executeGet ( $sql ) > 0) {
			while ( $row = $db->next () ) {
				array_push ( $mainrow ["primitive"], $row );
			}
		}
		
		$sql = "SELECT enableddetectors.detectorid, enableddetectors.detectorname,
			enableddetectors.validitystart, enableddetectors.validityend
			FROM enableddetectors WHERE run_id=" . $_GET ['run_id'] . " ORDER BY validitystart";
		// Fill the array with data
		$mainrow ["enableddetectors"] = Array ();
		if ($db->executeGet ( $sql ) > 0) {
			while ( $row = $db->next () ) {
				array_push ( $mainrow ["enableddetectors"], $row );
			}
		}
		
		return $mainrow;
	} else {
		die ( "No data in database" );
	}
}
function fetch_comment($db, $runID) {
	// Get data from DB
	$sql = "SELECT run.id, run.number, run.usercomment
		FROM run WHERE run.id=" . $runID;
	
	// Fill the array with data
	if ($db->executeGet ( $sql ) > 0) {
		return $db->next ();
	}
}
function fetch_xml($db, $runID) {
	$sql = "SELECT run.number FROM run WHERE run.id=" . $runID;
	if ($db->executeGet ( $sql ) > 0) {
		$dbres = $db->next ();
		return $dbres;
	} else {
		die ( "No data in database" );
	}
}
function prepare_enabled($type, $record) {
	if ($type == "all")
		return str_replace ( "+", " ", $record ['enabledstring'] );
	else if ($type == "search")
		return implode ( " ", $record ["enableddetectors"] );
}
function prepare_trigger($type, $record) {
	if ($type == "all")
		return str_replace ( "+", "<br>", trim ( $record ['triggerstring'], '+' ) );
	else if ($type == "search") {
		$trigger = Array ();
		// Periodic trigger
		if (sizeof ( $record ["periodic"] ) > 0)
			array_push ( $trigger, "Period:" . implode ( ",", $record ["periodic"] ) );
			// Calibration trigger
		if ($record ["calibration"] == True)
			array_push ( $trigger, "Calib" );
			// Synchronisation trigger
		if ($record ["sync"] == True)
			array_push ( $trigger, "Sync" );
			// NIM trigger
		$NIMArray = Array ();
		foreach ( $record ['NIM'] as $value ) {
			$detArray = Array ();
			if (! is_null ( $value ['det_0'] ))
				array_push ( $detArray, $value ["det_0"] );
			if (! is_null ( $value ['det_1'] ))
				array_push ( $detArray, $value ["det_1"] );
			if (! is_null ( $value ['det_2'] ))
				array_push ( $detArray, $value ["det_2"] );
			if (! is_null ( $value ['det_3'] ))
				array_push ( $detArray, $value ["det_3"] );
			if (! is_null ( $value ['det_4'] ))
				array_push ( $detArray, $value ["det_4"] );
			array_push ( $NIMArray, implode ( "x", $detArray ) . "/" . $value ["triggernimdownscaling"] . "(" . $value ["triggernimreference"] . ")" );
		}
		if (sizeof ( $NIMArray ) > 0)
			array_push ( $trigger, "NIM:" . implode ( "+", $NIMArray ) );
			// Primitive trigger
		$PrimArray = Array ();
		foreach ( $record ['Primitive'] as $value ) {
			$detArray = Array ();
			if (! is_null ( $value ['maskA'] ))
				array_push ( $detArray, $value ["maskA"] );
			if (! is_null ( $value ['maskB'] ))
				array_push ( $detArray, $value ["maskB"] );
			if (! is_null ( $value ['maskC'] ))
				array_push ( $detArray, $value ["maskC"] );
			if (! is_null ( $value ['maskD'] ))
				array_push ( $detArray, $value ["maskD"] );
			if (! is_null ( $value ['maskE'] ))
				array_push ( $detArray, $value ["maskE"] );
			if (! is_null ( $value ['maskF'] ))
				array_push ( $detArray, $value ["maskF"] );
			if (! is_null ( $value ['maskG'] ))
				array_push ( $detArray, $value ["maskG"] );
			array_push ( $PrimArray, implode ( "x", $detArray ) . "/" . $value ["triggerprimitivedownscaling"] . "(" . $value ["triggerprimitivereference"] . ")" );
		}
		if (sizeof ( $PrimArray ) > 0)
			array_push ( $trigger, "Primitive:" . implode ( "<br>", $PrimArray ) );
		return implode ( "<br>", $trigger );
	}
}
function fetch_PrimitivesTypes($db) {
	$primArray = array (
			1 => array () 
	);
	
	// Get data from DB (1 detector)
	$sql = "SELECT d0.detname AS triggertype
		FROM primitivedetname as d0
		WHERE d0.detname<>''";
	// Fill the array with data
	$db->executeGet ( $sql );
	while ( $row = $db->next () ) {
		array_push ( $primArray [1], $row ["triggertype"] );
	}
	
	// Get data from DB (2 detectors)
	$primArray [2] = prepare_PrimCorrelationSQL ( $db, 2 );
	// Get data from DB (3 detectors)
	$primArray [3] = prepare_PrimCorrelationSQL ( $db, 3 );
	// Get data from DB (4 detectors)
	$primArray [4] = prepare_PrimCorrelationSQL ( $db, 4 );
	// Get data from DB (5 detectors)
	$primArray [5] = prepare_PrimCorrelationSQL ( $db, 5 );
	// Get data from DB (6 detectors)
	$primArray [6] = prepare_PrimCorrelationSQL ( $db, 6 );
	// Get data from DB (7 detectors)
	$primArray [7] = prepare_PrimCorrelationSQL ( $db, 7 );
	
	return $primArray;
}
function prepare_PrimCorrelationSQL($db, $nCombi) {
	$fieldsArray = array ();
	$tablesArray = array ();
	$stCond = array ();
	for($i = 0; $i < $nCombi; $i ++) {
		$fieldsArray ["d" . $i] = "d" . $i . ".detname";
		$tablesArray ["d" . $i] = "primitivedetname AS d" . $i;
	}
	for($i = 0; $i < sizeof ( $fieldsArray ) - 1; $i ++) {
		array_push ( $stCond, $fieldsArray ["d" . $i] . "<" . $fieldsArray ["d" . ($i + 1)] );
	}
	$sql = "SELECT CONCAT_WS('x', " . implode ( ",", $fieldsArray ) . ") AS triggertype " . "FROM " . implode ( " JOIN ", $tablesArray ) . " ON " . implode ( "<>'' AND ", $fieldsArray ) . "<>'' AND " . implode ( " AND ", $stCond );
	
	$db->executeGet ( $sql );
	$resArray = array ();
	while ( $row = $db->next () ) {
		array_push ( $resArray, $row ["triggertype"] );
	}
	return $resArray;
}
function fetch_PrimitiveTypeForDet($db, $index) {
	$sql = "SELECT * FROM primitivedetname WHERE detnumber=" . $index . " AND detname<>''";
	$db->executeGet ( $sql );
	$typeArray = array ();
	while ( $row = $db->next () ) {
		array_push ( $typeArray, array (
				$row ["detmask"],
				base_convert ( $row ["detmask"], 16, 2 ),
				$row ["detname"] 
		) );
	}
	
	return $typeArray;
}
function maxArrayArraySize($myArray) {
	$max = 0;
	foreach ( $myArray as $arr ) {
		$elSize = sizeof ( $arr );
		if ($elSize > $max)
			$max = $elSize;
	}
	return $max;
}
function invert2DArrray($myArray) {
	$maxArray = maxArrayArraySize ( $myArray );
	$invertedArray = array ();
	for($i = 0; $i < $maxArray; $i ++) {
		$invertedArray [$i] = array ();
		for($el = 0; $el < 7; $el ++) {
			if (isset ( $myArray [$el] [$i] ))
				array_push ( $invertedArray [$i], $myArray [$el] [$i] );
			else
				array_push ( $invertedArray [$i], array (
						0 => "",
						1 => "" 
				) );
		}
	}
	return $invertedArray;
}
function fetch_PrimitiveMaskTypes($db) {
	$detArray = array ();
	
	for($i = 0; $i < 7; $i ++) {
		$detArray [$i] = fetch_PrimitiveTypeForDet ( $db, $i );
	}
	
	// $triggerArray = invert2DArrray ( $detArray );
	
	return $detArray;
}