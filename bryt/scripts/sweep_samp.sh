#!/bin/bash

set -x

RERUN=$1

mkdir -p results-samp


while IFS= read -r line; do
    read -r mode model <<< "$line"
    echo "==== Running $model $mode $samp ===="
    python -m bryt.sampling_bench $mode $model > results-samp/samp.$model.$mode.out
done < "bryt/models_all.txt"

