# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the Flexiv robots.

The following configurations are available:

* :obj:`FLEXIV_RIZON4S_CFG`: Flexiv Rizon 4s robot with Grav gripper
* :obj:`FLEXIV_RIZON4S_HIGH_PD_CFG`: Flexiv Rizon 4s robot with stiffer PD control

Reference:  https://github.com/flexivrobotics/isaac_sim_ws
"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
import pathlib

##
# Configuration
##


CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
FLEXIV_USD_PATH = str(CURRENT_DIR / "data" / "flexiv" / "Rizon4s_with_Grav.usd")

FLEXIV_RIZON4S_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=FLEXIV_USD_PATH,
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True, solver_position_iteration_count=8, solver_velocity_iteration_count=0
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "joint1": 0.0,
            "joint2": -0.569,
            "joint3": 0.0,
            "joint4": -2.810,
            "joint5": 0.0,
            "joint6": 3.037,
            "joint7": 0.741,
            "finger_joint": 0.04,
        },
    ),
    actuators={
        "flexiv_shoulder":  ImplicitActuatorCfg(
            joint_names_expr=["joint[1-4]"],
            effort_limit_sim=87.0,
            stiffness=80.0,
            damping=4.0,
        ),
        "flexiv_forearm": ImplicitActuatorCfg(
            joint_names_expr=["joint[5-7]"],
            effort_limit_sim=12.0,
            stiffness=80.0,
            damping=4.0,
        ),
        "flexiv_gripper": ImplicitActuatorCfg(
            joint_names_expr=["finger_joint"],
            effort_limit_sim=200.0,
            stiffness=2e3,
            damping=1e2,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
"""Configuration of Flexiv Rizon 4s robot with Grav gripper."""


FLEXIV_RIZON4S_HIGH_PD_CFG = FLEXIV_RIZON4S_CFG.copy()
FLEXIV_RIZON4S_HIGH_PD_CFG.spawn.rigid_props.disable_gravity = True
FLEXIV_RIZON4S_HIGH_PD_CFG.actuators["flexiv_shoulder"].stiffness = 400.0
FLEXIV_RIZON4S_HIGH_PD_CFG.actuators["flexiv_shoulder"].damping = 80.0
FLEXIV_RIZON4S_HIGH_PD_CFG.actuators["flexiv_forearm"].stiffness = 400.0
FLEXIV_RIZON4S_HIGH_PD_CFG.actuators["flexiv_forearm"].damping = 80.0
"""Configuration of Flexiv Rizon 4s robot with stiffer PD control.

This configuration is useful for task-space control using differential IK.
"""
