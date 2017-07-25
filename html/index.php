
<html>
<head>
<meta http-equiv="refresh" content="20">
</head>

<body>
<?php include('more.html') ?>

<pre>
<?php


$check="ps -aux | grep OG";
$escapes0="grep 'Current rank' ~/og_log_ur.txt | tail -1 && grep Incoming ~/og_log_ur.txt -A 3 | tail -n +0 | tail -n 30 | tac";
$escapes1="grep 'Current rank' ~/og_log_libra.txt | tail -1 && grep Incoming ~/og_log_libra.txt -A 3 | tail -n +0 | tail -n 30 | tac";
$escapes2="grep 'Current rank' ~/og_log_vi* | tail -1 && grep Incoming ~/og_log_vi* -A 3 | tail -n +0 | tail -n 30 | tac";
$escapes3="grep 'Current rank' ~/og_log_rh* | tail -1 && grep Incoming ~/og_log_rh* -A 3 | tail -n +0 | tail -n 30 | tac";

date_default_timezone_set('Europe/Paris');


$now = new DateTime();
echo $now->format('Y-m-d H:i:s');

echo '  <a href="/log" target="_blank">logs</a>';

echo "\n\n\nCurrently running : ";

//passthru( $check, $out );
exec( $check, $out );

$vals = array('libra','uriel','rhea','virgo');

foreach ($out as $line) {
	foreach ($vals as $val) {

		if ( strstr($line, $val) ) {
			$$val = true;
		}

	}
}


foreach ($vals as $val) {
	if ($$val) {
		echo $val . " ";
	}
}


echo "\n\n\nLatest escapes :\n\n";

echo "Uriel\n\n";
passthru( $escapes0 );

echo "\n\nLibra\n\n";
passthru( $escapes1 );

echo "\n\nVirgo\n\n";
passthru( $escapes2 );

echo "\n\nRhea\n\n";
passthru( $escapes3 );


echo '</pre>';

?>


</body>
</html>

