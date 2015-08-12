#!/usr/bin/perl -w

if ($#ARGV!=1) {
    print "usage: convert.pl file_name i\n";
    exit 1;
}

$file_name = $ARGV[0];
$tel_req = $ARGV[1];

open INPUT, $file_name or die "Cannot open $file_name";
while (<INPUT>) {
    @f=split;
    if ($#f == 2) {
	($gch, $t0) = ($f[0], $f[2]);
	$tel = int($gch/512);
	if ($tel == $tel_req) {
	    $tdcb = int(($gch % 512)/128);
	    $tdc = int(($gch % 128)/32);
	    $ch = $gch % 32;
	    if (abs($t0) < 500) {
		print "$tdcb $tdc $ch $f[2]\n";
	    }
	}
    }
}
