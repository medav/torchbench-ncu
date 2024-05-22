#!/bin/bash

NCU_PATH=ncu

$NCU_PATH \
    --target-processes all \
    --profile-from-start no \
    --csv \
    --metrics gpu__time_duration.sum,sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed,gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed,sm__throughput.avg.pct_of_peak_sustained_elapsed \
    $*

