# Copyright (c) 2022-2025, The Isaac Lab Project Developers
# SPDX-License-Identifier: BSD-3-Clause

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

# CRITICAL: Point to the new FIXED file you just generated
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
            # Keep False for now. Once training works, you can try True if you need self-collision.
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # Safe "Candle/Home" pose.
        # (Franka's -2.81 on joint4 would crash this robot)
        joint_pos={
            "joint1": 0.0,
            "joint2": -0.5,
            "joint3": 0.0,
            "joint4": 1.5,
            "joint5": 0.0,
            "joint6": 0.5,
            "joint7": 0.0,
            # Gripper is Revolute: 0.0 is Open
            "finger_joint": 0.0,
        },
    ),
    actuators={
        "flexiv_arm": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-7]"],
            effort_limit_sim=100.0,
            velocity_limit_sim=2.0,
            stiffness=400.0,   # Good stiffness for RL
            damping=40.0,
        ),
        "gripper": ImplicitActuatorCfg(
            # Control the driver joint. The patched USD removed the hostile internal drive.
            joint_names_expr=["finger_joint"],
            effort_limit=40.0,
            effort_limit_sim=40.0,
            velocity_limit_sim=2.0,
            stiffness=800.0,   # Stiff enough to hold the cube
            damping=40.0,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)