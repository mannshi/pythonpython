#!/bin/bash

answer[1]=66
answer[2]=109
answer[3]=10
answer[4]=96
answer[5]=7
answer[6]=5
answer[7]=8
answer[8]=30
answer[9]=135
answer[10]=135
answer[11]=5
answer[12]=123

for n in {1..12};do
    num=`printf "%02d" $n`
	tdir=v
    ifile=$tdir/$num.c
    afile=$tdir/$num.s
    efile=$tdir/$num.exe
	pfile=$tdir/myp.o

    echo TEST$num; ( /usr/bin/python3 main.py $ifile > $afile ); gcc -g -o $efile $afile $pfile ; ./$efile ;echo execute $?; echo expect ${answer[$n]}
done
