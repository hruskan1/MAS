#!/bin/bash

for path in ../hw1/efg_2023/games/*.efg; do
    
    filename=$(echo $path| cut -d'/' -f 5 | cut -d '.' -f 1)
    echo "python $1 < $path > ../hw1/efg_2023/computed_values/$filename.txt"
    #touch ../hw1/efg_2023/computed_values/$filename.txt
    conda run -n mas python $1 < $path 

    #diff ../hw1/efg_2023/computed_values/$filename.txt ../hw1/efg_2023/values/$filename.txt
    break
done
