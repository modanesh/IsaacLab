#!/bin/bash

declare -A RUNS=(
  [Isaac-Velocity-Rough-Anymal-D-Play-v0]="2025-07-02_16-27-40_anymal_d_rough 2025-07-02_17-31-33_anymal_d_rough 2025-07-02_18-36-01_anymal_d_rough 2025-07-02_19-40-17_anymal_d_rough 2025-07-02_20-44-25_anymal_d_rough"
  [Isaac-Velocity-Flat-Anymal-D-Play-v0]="2025-07-02_21-49-02_anymal_d_flat 2025-07-02_21-53-11_anymal_d_flat 2025-07-02_21-57-19_anymal_d_flat 2025-07-02_22-01-30_anymal_d_flat 2025-07-02_22-05-40_anymal_d_flat"
  [Isaac-Velocity-Rough-Anymal-C-Play-v0]="2025-07-02_22-09-46_anymal_c_rough 2025-07-02_23-13-17_anymal_c_rough 2025-07-03_00-16-36_anymal_c_rough 2025-07-03_01-19-50_anymal_c_rough 2025-07-03_02-23-35_anymal_c_rough"
  [Isaac-Velocity-Flat-Anymal-C-Play-v0]="2025-07-03_03-27-09_anymal_c_flat 2025-07-03_03-30-47_anymal_c_flat 2025-07-03_03-34-25_anymal_c_flat 2025-07-03_03-38-03_anymal_c_flat 2025-07-03_03-41-39_anymal_c_flat"
  [Isaac-Velocity-Rough-Anymal-B-Play-v0]="2025-07-03_03-45-16_anymal_b_rough 2025-07-03_04-46-09_anymal_b_rough 2025-07-03_05-50-05_anymal_b_rough 2025-07-03_06-56-25_anymal_b_rough 2025-07-03_08-04-22_anymal_b_rough"
  [Isaac-Velocity-Flat-Anymal-B-Play-v0]="2025-07-03_09-13-13_anymal_b_flat 2025-07-03_09-18-45_anymal_b_flat 2025-07-03_09-24-04_anymal_b_flat 2025-07-03_09-29-33_anymal_b_flat 2025-07-03_09-33-44_anymal_b_flat"
  [Isaac-Velocity-Flat-Unitree-Go1-Play-v0]="2025-07-03_09-37-59_unitree_go1_flat 2025-07-03_09-41-37_unitree_go1_flat 2025-07-03_09-45-13_unitree_go1_flat 2025-07-03_09-48-50_unitree_go1_flat 2025-07-03_09-52-20_unitree_go1_flat"
  [Isaac-Velocity-Rough-Unitree-Go1-Play-v0]="2025-07-03_10-54-43_unitree_go1_rough 2025-07-03_11-59-12_unitree_go1_rough 2025-07-03_13-06-40_unitree_go1_rough 2025-07-03_14-19-00_unitree_go1_rough 2025-07-03_15-25-37_unitree_go1_rough"
  [Isaac-Velocity-Flat-Unitree-Go2-Play-v0]="2025-07-03_16-39-35_unitree_go2_flat 2025-07-03_16-43-49_unitree_go2_flat 2025-07-03_16-48-12_unitree_go2_flat 2025-07-03_16-52-27_unitree_go2_flat 2025-07-03_16-56-02_unitree_go2_flat"
  [Isaac-Velocity-Rough-Unitree-Go2-Play-v0]="2025-07-03_17-54-38_unitree_go2_rough 2025-07-03_19-44-12_unitree_go2_rough 2025-07-03_21-30-26_unitree_go2_rough 2025-07-03_23-18-51_unitree_go2_rough 2025-07-04_01-07-18_unitree_go2_rough"
  [Isaac-Velocity-Flat-Unitree-A1-Play-v0]="2025-07-04_02-55-49_unitree_a1_flat 2025-07-04_02-58-59_unitree_a1_flat 2025-07-04_03-02-03_unitree_a1_flat 2025-07-04_03-05-07_unitree_a1_flat 2025-07-04_03-08-13_unitree_a1_flat"
  [Isaac-Velocity-Rough-Unitree-A1-Play-v0]="2025-07-04_03-11-19_unitree_a1_rough 2025-07-04_03-40-12_unitree_a1_rough 2025-07-04_04-09-04_unitree_a1_rough 2025-07-04_04-39-00_unitree_a1_rough 2025-07-04_05-08-04_unitree_a1_rough"
  [Isaac-Velocity-Flat-Spot-Play-v0]="2025-07-04_05-37-04_spot_flat 2025-07-04_10-30-21_spot_flat 2025-07-04_13-57-42_spot_flat 2025-07-04_17-28-24_spot_flat 2025-07-04_20-41-47_spot_flat"
)

for TASK in "${!RUNS[@]}"; do
  for RUN_ID in ${RUNS[$TASK]}; do
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task="$TASK" --headless --num_envs=1024 --load_run="$RUN_ID"
  done
done
