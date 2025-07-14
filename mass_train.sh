#!/bin/bash

TASKS=(
  Isaac-Velocity-Rough-Anymal-D-v0
  Isaac-Velocity-Flat-Anymal-D-v0
  Isaac-Velocity-Rough-Anymal-C-v0
  Isaac-Velocity-Flat-Anymal-C-v0
  Isaac-Velocity-Rough-Anymal-B-v0
  Isaac-Velocity-Flat-Anymal-B-v0
  Isaac-Velocity-Flat-Unitree-Go1-v0
  Isaac-Velocity-Rough-Unitree-Go1-v0
  Isaac-Velocity-Flat-Unitree-Go2-v0
  Isaac-Velocity-Rough-Unitree-Go2-v0
  Isaac-Velocity-Flat-Unitree-A1-v0
  Isaac-Velocity-Rough-Unitree-A1-v0
  Isaac-Velocity-Flat-Spot-v0
)

for TASK in "${TASKS[@]}"; do
  for SEED in {1..5}; do
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task="$TASK" --headless --seed="$SEED"
  done
done
