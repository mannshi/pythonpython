#!/bin/bash

answer[1]=1
answer[2]=3
answer[3]=46
answer[4]=13
answer[5]=13
answer[6]=0

for n in {1..6};do
	num=`printf "%02d" $n`
	ifile=testi$num.c
	afile=testi$num.s
	efile=testi$num.exe
	
	echo TEST$num; ( /usr/bin/python3 mannc.py $ifile > $afile ); gcc -o $efile $afile ; ./$efile ;echo execute $?; echo expect ${answer[$n]}
done
