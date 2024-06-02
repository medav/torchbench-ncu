import torch
import importlib
import sys
import time
import os


net = torch.nn.Linear(512, 512, bias=False).cuda().half()
x = torch.randn(512, 512, device='cuda', dtype=torch.float16)

roi = lambda: net(x)

with torch.cuda.profiler.profile():
    t0 = time.perf_counter()
    roi()
    t1 = time.perf_counter()


print(f'Runtime: {t1 - t0}')
