#!/bin/bash

./bryt/scripts/build-docker.sh
docker run --gpus all --rm -it -v $(pwd):/work bryt bash
