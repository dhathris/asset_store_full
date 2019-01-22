#!/bin/bash

file=`cat ./requirements.txt`

while IFS= read -r line;
do
    names=`echo $line | tr "==" "\n"`
    name=`echo $names | cut -d" " -f1`
    list=`pip list | grep $name`
    if [ -z "$list" ];
    then
        pip install $line
    else
        echo "$list is already installed on the system"
    fi
done <<< "$file"
