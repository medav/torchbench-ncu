# BRYT Instructions

## 1. Build the Docker Container
```bash
host $ ./bryt/scripts/build-docker.sh
```

## 2. Start the Docker Container
```bash
host $ ./bryt/scripts/run-docker.sh
```

## 3. Run the Sweep Check (To make sure things work)
```bash
container $ ./bryt/scripts/sweep_check.sh
```


## 4. Run the NCU Sweep
```bash
container $ ./bryt/scripts/sweep_ncu.sh
```
