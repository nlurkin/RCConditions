<html>
<head>
<title>NA62 Status</title>
</head>
<body>
<?php
$filename = 'images/Environment.png';
if (file_exists($filename)) {
   echo "Content was generated on : " . date ("F d Y H:i:s.", filemtime($filename));
}
?>
<img src="images/Environment.png" width="100%"/>
</body>
</html>
