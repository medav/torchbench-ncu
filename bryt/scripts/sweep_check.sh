#!/bin/bash

RERUN=$1

mkdir -p results

while IFS= read -r line; do
    read -r mode model <<< "$line"

    echo "==== Running $model $mode ===="

    python bryt/run_wrapper.py $mode $model 1 > results/profile.$model.$mode.out 2> results/profile.$model.$mode.err
    [ $? -eq 0 ] && rm results/profile.$model.$mode.err && rm results/profile.$model.$mode.out
done < "bryt/models_all.txt"
