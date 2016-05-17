#!/bin/sh

lastExport=`cat .lastExport`
lastRun=`ls -1v /afs/cern.ch/user/n/nlurkin/www/NA62/XMLProcessed/ | tail -n 1 | cut -d "." -f 1`

cd /home/nlurkin/RCConditions
for run in $(seq $lastExport $lastRun); do
	mkdir /afs/cern.ch/user/n/na62prod/offline/XML/Run$run
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
