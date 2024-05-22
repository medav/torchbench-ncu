#!/bin/bash

set -x

RERUN=$1

mkdir -p results


while IFS= read -r line; do
    read -r mode model <<< "$line"
    echo "==== Running $model $mode ===="
    ./bryt/ncu.sh python bryt/run_wrapper.py $mode $model 1 > results/ncu.$model.$mode.out
done < "bryt/models_all.txt"

