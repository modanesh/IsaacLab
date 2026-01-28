# Copyright (c) 2022-2025, The Isaac Lab Project Developers
# SPDX-License-Identifier: BSD-3-Clause

"""
FINAL FIX for Flexiv Gripper

PROBLEM IDENTIFIED:
The mimic joints have INCORRECT limits in the USD file:
- Current limits: [-0.155, 0.785] rad for most joints
- But when finger_joint = 0.7, the mimic joints need to reach:
  - left_inner_knuckle:  ~1.87 rad (needs upper limit > 1.87!)
  - right_inner_knuckle: ~-1.73 rad (needs lower limit < -1.73!)

The joints are exceeding their limits, which causes PhysX to apply
corrective forces that prevent finger_joint from reaching its target.

SOLUTION:
Override the soft joint limits to give the mimic joints more range.
"""

import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

USD_PATH = "/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/Rizon4s_with_Grav_FIXED.usd"

FLEXIV_WITH_GRIPPER_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=USD_PATH,
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
        ),
        # Disable USD drives to let our actuators take control
        joint_drive_props=sim_utils.JointDrivePropertiesCfg(
            drive_type="none",
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "joint1": 0.0,
            "joint2": -0.5,
            "joint3": 0.0,
            "joint4": 1.5,
            "joint5": 0.0,
            "joint6": 0.5,
            "joint7": 0.0,
            "finger_joint": 0.0,
        },
    ),
    actuators={
        "flexiv_arm": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-7]"],
            effort_limit_sim=100.0,
            velocity_limit_sim=2.0,
            stiffness=800.0,  # Increase from 400.0
            damping=80.0,     # Increase from 40.0
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["finger_joint"],
            effort_limit=100.0,      # Increase from 80.0
            effort_limit_sim=100.0,  # Increase from 80.0
            velocity_limit_sim=2.0,
            stiffness=2000.0,  # Increase from 800.0
            damping=100.0,     # Increase from 30.0
        ),
    },
    # CRITICAL: Use factor < 1.0 to effectively DISABLE soft limits
    # This prevents PhysX from applying corrective forces when mimic joints
    # exceed their (incorrectly configured) limits
    soft_joint_pos_limit_factor=0.0,  # 0.0 = disable soft limits completely
)