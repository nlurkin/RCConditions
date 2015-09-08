<?php

// DB transactions class
class DBConnect {
	var $connection;
	var $resultPtr;
	
	// Init connection to DB
	function init($serverName, $userName, $password, $dbName, $port){
		$this->connection = new mysqli($serverName, $userName, $password, $dbName, $port);
		if($this->connection->connect_error){
			return false;
		}
		return true;
	}
	
	function getError(){
		return $this->connection->connect_error;
	}
	function executeGet($sql){
		$this->resultPtr = $this->connection->query($sql);
		if(!$this->resultPtr){
			Die("SQL request failed: " . $sql);
		}
		return $this->resultPtr->num_rows;
	}
	
	function next(){
		return $this->resultPtr->fetch_assoc();
	}
	
	function close(){
		$this->connection->close();
	}
	
	function executeUpdate($sqlCmd, $typeString){
		//Update data in DB
		if( !($sql = $this->connection->prepare($sqlCmd))){
			echo "Prepare failed: (" . $this->connection->errno.") " . $this->connection->error;
			return false;
		}
		
		$inArgs = func_get_args();
		$args = Array();
		$args[0] = $typeString;
		foreach($inArgs as $key => $n){
			if($key<2) continue;
			$args[$key-1] = &$inArgs[$key];
		}
		
		if(!call_user_func_array(array($sql, "bind_param"), $args)){
			echo "Binding parameters failed: (" . $sql->errno . ") ".$sql->error;
			return false;
		}
		
		if(!$sql->execute()){
			echo "Execute failed: (" . $sql->errno . ") ".$sql->error;
			return false;
		}
		
		return true;
	}
}

// Some useful functions
function humanReadable($value, $units, $precision=-1){
	$i=0;
	while($value >= 1000 and $i<count($units)-1){
		$value /= 1000.;
		$i=$i+1;
	}
	
	if($precision!=-1) $value = round($value, $precision);
	return $value." ".$units[$i];
}

function is_url_exist($url){
	$ch = curl_init($url);    
	curl_setopt($ch, CURLOPT_NOBODY, true);
	curl_exec($ch);
	$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

	if($code == 200){
		$status = true;
	}else{
		$status = false;
	}
	curl_close($ch);
	return $status;
}

function exists($path){
	if(strpos($path, "http://")===false) return file_exists($path);
	else return is_url_exist($path);
}
