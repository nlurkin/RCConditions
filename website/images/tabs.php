<html> 
<body>
	<title>NA62 Tabbed Panels</title>
	
<style type="text/css"> 
	
	.tdtitle {
        padding:5px;
        background-color:#486090;
        color:white;
        border:2px solid #000040;
        border-top:2px solid #E0E0E0;
        border-bottom:2px solid #000040;
        border-left:2px solid #000080;
        }
        
	#Tabs ul {
	padding: 0px;
	margin: 0px;
	margin-left: 10px;
	list-style-type: none;
	}
	
	#Tabs ul li {
	display: inline-block;
	clear: none;
	float: left;
	height: 24px;
	}
	
	#Tabs ul li a {
	position: relative;
	text-align:center;
	margin-top: 20px;
	display: block;
	margin-left: 12px;
	line-height: 30px;
	background: #486090;
	z-index: 9999;
	border: 1px solid #ccc;
	border-bottom: 0px;
	
	/* The following four lines are to make the top left and top right corners of each tab rounded. */
	-moz-border-radius-topleft: 6px;
	border-top-left-radius: 6px;
	-moz-border-radius-topright: 6px;
	border-top-right-radius: 6px;
	/* end of rounded borders */
	
	width: 200px;
	color: #FFFFFF;
	font-size:20px;
	text-decoration: none;
	font-weight: bold;
	}
	
	#Tabs ul li a:hover {
	text-decoration: underline; // a very simple effect when hovering the mouse on tab
	}
	
	#Tabs #Content_Area { // this is the css class for the content displayed in each tab
	padding: 15px;
	clear:both;
	overflow:visible;
	line-height:22px;
	position: relative;
	top: 40px;
	z-index: 5;
	height: 150px;
	overflow: visible;
	}
	
	p { padding-left: 15px; }

</style>
	<table width=100% border=0 cellpadding=3 cellspacing=0> 
          <tr style="position:relative"> 
            <td class="tdtitle" align=center> 
              <span style="font-size:52px">NA62 Panel List</span><img border=0 align=right src="NA62logo.gif" alt="NA62 logo" height="100px">  
            </td> 
          </tr> 
        </table>  
	<div id="Tabs">
		<ul>
			<li id="li_tab1" onclick="tab('tab1')" ><a>Run Control</a></li>
			<li id="li_tab2" onclick="tab('tab2')" ><a>Environment Monitor</a></li>
			<li id="li_tab3" onclick="tab('tab3')" ><a>Main DCS Display</a></li>
		</ul>
		<div id="Content_Area">
			<div id='tab1'> <img border=0 align=center src="bigScreen.png" alt="bigScreen Panel" width="1200" height="600" ></div>
			<div id='tab2' style="display: none;"> <img border=0 align=center src="Environment.png" alt="Environment panel" width="1200" height="600"></div>
			<div id='tab3' style="display: none;"> <img border=0 align=center src="MainDCS.png" alt="Main DCS Panel" width="1200" height="600"></div>
<?php $filename = "bigScreen.png";
if (file_exists($filename)) {
echo "Content was generated on : " . date ("F d Y H:i:s.", filemtime($filename));
}
?>
		</div> <!– End of Content_Area Div –>
	</div> <!– End of Tabs Div –>


	<script type="text/javascript">
		function tab(tab) {
		document.getElementById('tab1').style.display = 'none';
		document.getElementById('tab2').style.display = 'none';
		document.getElementById('tab3').style.display = 'none';
		document.getElementById('li_tab1').setAttribute("class", "");
		document.getElementById('li_tab2').setAttribute("class", "");
		document.getElementById('li_tab3').setAttribute("class", "");
		document.getElementById(tab).style.display = 'block';
		document.getElementById('li_'+tab).setAttribute("class", "active");
		}

	</script>   

</body>


</html>	
