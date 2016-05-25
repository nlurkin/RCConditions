#!/bin/sh
cd /home/nlurkin/RCConditions

lastExport=`cat .lastExport`
lastRun=`ls -1v /afs/cern.ch/user/n/nlurkin/www/NA62/XMLProcessed/ | tail -n 1 | cut -d "." -f 1`

for run in $(seq $lastExport $lastRun); do
	if [ ! -d "/afs/cern.ch/user/n/na62prod/offline/XML/Run$run" ]; then
		mkdir /afs/cern.ch/user/n/na62prod/offline/XML/Run$run
	fi
	./configRead.py -r $run --dumpinit
	echo $run > .lastExport
done

#Remove old runs
let "removeBefore = $lastRun - 50"

listDir=`ls -1v /afs/cern.ch/user/n/na62prod/offline/XML/`

for dir in $listDir; do
	runNum=${dir:3}
	if [ $runNum -lt $removeBefore ]; then
		rm -r /afs/cern.ch/user/n/na62prod/offline/XML/$dir
	fi
done
