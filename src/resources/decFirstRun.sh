#!/bin/bash
while IFS='' read -r line || [[ -n "$line" ]]; do
    if [ "$line" = true ] ; then
        break
    else 
        do something
    fi
done < "$1"