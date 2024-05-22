#!/bin/bash


while IFS= read -r line; do
    read -r mode model <<< "$line"
    echo python bryt/run_wrapper.py $mode $model 1
done < "bryt/models_all.txt"

