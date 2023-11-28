#!/bin/bash

for path in ./efg_2023/caves/*.txt; do
    
    filename=$(echo $path| cut -d'/' -f 4 | cut -d '.' -f 1)
    echo $filename
    
    python $1 < $path > ./efg_2023/games/$filename.efg
    break
done
