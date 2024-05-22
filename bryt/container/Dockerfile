FROM nvcr.io/nvidia/pytorch:24.04-py3
WORKDIR /root

RUN apt update
RUN apt upgrade -y

RUN apt install -y wget build-essential
# RUN apt install -y nsight-systems-2023.4.4

RUN wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh && \
    bash Anaconda3-2024.02-1-Linux-x86_64.sh -b && \
    rm Anaconda3-2024.02-1-Linux-x86_64.sh

RUN ~/anaconda3/bin/conda init

RUN /bin/bash -c "source /root/anaconda3/bin/activate && python -m pip install torch torchvision torchaudio"

RUN apt install -y git
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN git clone https://github.com/medav/torchbench-ncu.git
RUN /bin/bash -c "source /root/anaconda3/bin/activate && cd torchbench-ncu && python install.py"

WORKDIR /work
ENTRYPOINT /bin/bash
