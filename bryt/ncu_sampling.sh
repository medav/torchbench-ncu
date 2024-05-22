#!/bin/bash

SAMP=${SAMP:-all}

case $SAMP in
    all)
        SAMP_NCU_FLAG=""
        ;;
    10th)
        SAMP_NCU_FLAG='--kernel-id :::0|.*0'
        ;;
    20th)
        SAMP_NCU_FLAG='--kernel-id :::0|.*(2|4|6|8|0)0'
        ;;
    50th)
        SAMP_NCU_FLAG='--kernel-id :::0|.*(0|5)0'
        ;;
    100th)
        SAMP_NCU_FLAG='--kernel-id :::0|.*00'
        ;;
    *)
        echo "Unknown sampling mode: $SAMP"
        exit 1
        ;;
esac

NCU_PATH=${NCU_PATH:-/opt/nvidia/nsight-compute/2023.3.1/ncu}
METRICS=${METRICS:-gpu__time_duration.sum,sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed,gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed,sm__throughput.avg.pct_of_peak_sustained_elapsed}

$NCU_PATH \
    $SAMP_NCU_FLAG \
    --target-processes all \
    --profile-from-start no \
    --csv \
    --metrics $METRICS \
    $*


