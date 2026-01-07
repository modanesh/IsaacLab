# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the Flexiv robots.

The following configurations are available:

* : obj:`FLEXIV_RIZON4_CFG`: Flexiv Rizon 4 robot
* :obj:`FLEXIV_RIZON4_HIGH_PD_CFG`: Flexiv Rizon 4 robot with stiffer PD control

Reference:  https://github.com/flexivrobotics/isaac_sim_ws

Joint Limits (in radians):
    - joint1: [-2.792, 2.792]  (±160°)
    - joint2: [-2.269, 2.269]  (±130°)
    - joint3: [-2.967, 2.967]  (±170°)
    - joint4: [-1.867, 2.688]  (-107° to 154°)
    - joint5: [-2.967, 2.967]  (±170°)
    - joint6: [-1.396, 4.538]  (-80° to 260°)
    - joint7: [-2.967, 2.967]  (±170°)
"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

##
# Configuration
##

FLEXIV_WITH_GRIPPER_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path="/home/mohamad/Research/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/data/flexiv/flexiv_rizon4_with_Robotiq_2F_85_flattened.usd",
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
            "joint2": -0.6,
            "joint3": 0.0,
            "joint4": -1.5,
            "joint5": 0.0,
            "joint6": 1.0,
            "joint7": 0.0,
            "finger_joint": 0.04,
        },
    ),
    actuators={
        "flexiv_arm": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-7]"],
            effort_limit_sim=87.0,
            stiffness=80.0,
            damping=4.0,
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["finger_joint"],
            effort_limit_sim=200.0,
            stiffness=2e3,
            damping=1e2,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
"""Configuration of Flexiv Rizon 4 robot."""

FLEXIV_RIZON4_HIGH_PD_CFG = FLEXIV_RIZON4_CFG.copy()
FLEXIV_RIZON4_HIGH_PD_CFG.spawn.rigid_props.disable_gravity = True
FLEXIV_RIZON4_HIGH_PD_CFG.actuators["flexiv_shoulder"].stiffness = 400.0
FLEXIV_RIZON4_HIGH_PD_CFG.actuators["flexiv_shoulder"].damping = 80.0
FLEXIV_RIZON4_HIGH_PD_CFG.actuators["flexiv_forearm"].stiffness = 400.0
FLEXIV_RIZON4_HIGH_PD_CFG.actuators["flexiv_forearm"].damping = 80.0
"""Configuration of Flexiv Rizon 4 robot with stiffer PD control.

This configuration is useful for task-space control using differential IK.
"""
