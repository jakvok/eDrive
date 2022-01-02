<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>temperatures</title>
<meta http-equiv="Content-Language" content="us">
<meta http-equiv="Content-Type" content="text/html" charset="utf-8">



<style type="text/css">
<!--

body
	{
	font-family: tahoma, sans-serif;
	background-color: grey;
	text-align: left;
	}

.nadpis {
    font-size: 70px;
    font-weight: bold;

    }

.obsah
	{
	font-size: 32px;
	}

td
	{
	border: solid 1px black;
	font-size: 32px;
	text-align: center;
	}

.prvni
	{
	font-weight: bold;
	background-color: white;
	}



//-->
</style>

</head>

<body>

<span class="nadpis">TEMPERATURES RECORD</span>

<div class="obsah">
<br>
<span style="font-size: 40px;">
Indicated values [deg.C]:
</span>


<?php

//read array of recorded values

$pole = array();

$f = fopen("temper.csv","r");

while ( ($hhh = fgetcsv($f,600,";")) !== FALSE ) {

$pole[] = $hhh;

}

$pole = array_reverse($pole);

fclose($f);

?>



<table>
<tr><td>&nbsp;CAS</td><td> &nbsp;venku1&nbsp; </td><td> &nbsp;venku2&nbsp; </td><td> &nbsp;dilna&nbsp; </td><td> &nbsp;topeni&nbsp; </td></tr>

<tr class="prvni"><td><?php echo $pole[0][0] ?></td><td><?php echo $pole[0][1] ?></td><td><?php echo $pole[0][2] ?></td><td><?php echo $pole[0][3] ?></td><td><?php echo $pole[0][4] ?></td></tr>

<?php	

for($i=1;$i<count($pole);$i++) {
	
    	echo "<tr><td>".$pole[$i][0]."&nbsp;</td><td>".$pole[$i][1]."</td><td>".$pole[$i][2]."</td><td>".$pole[$i][3]."</td><td>".$pole[$i][4]."</td></tr>";

}

?>

	
</table>


</div>

</body>
</html>
