import torch
import importlib
import sys
import time
import os

os.environ['HUGGING_FACE_HUB_TOKEN'] = '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'

mode = sys.argv[1]
model = sys.argv[2]
ni = int(sys.argv[3])
sys.path.append(".")
model_name = f"torchbenchmark.models.{model}"
module = importlib.import_module(model_name)

benchmark_cls = getattr(module, "Model", None)
benchmark = benchmark_cls(test=mode, device="cuda")

if not hasattr(benchmark, 'train'):
    def train():
        loss = benchmark.forward()
        benchmark.get_optimizer().zero_grad()
        benchmark.backward(loss)
        benchmark.optimizer_step()

    benchmark.train = train

if mode == "train":
    roi = lambda: benchmark.train()
elif mode == "eval":
    roi = lambda: benchmark.eval()

roi()

with torch.cuda.profiler.profile():
    t0 = time.perf_counter()
    for _ in range(ni): roi()
    t1 = time.perf_counter()


print(t1 - t0)
