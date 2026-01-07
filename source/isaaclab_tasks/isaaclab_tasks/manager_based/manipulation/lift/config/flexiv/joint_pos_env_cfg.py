# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from isaaclab.assets import RigidObjectCfg
from isaaclab.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from isaaclab.utils import configclass
from isaaclab_assets.robots.flexiv import FLEXIV_WITH_GRIPPER_CFG

from isaaclab_tasks.manager_based.manipulation.lift import mdp
from isaaclab_tasks.manager_based.manipulation.lift.lift_env_cfg import LiftEnvCfg

@configclass
class FlexivCubeLiftEnvCfg(LiftEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # Use the combined Flexiv + Robotiq configuration
        self.scene.robot = FLEXIV_WITH_GRIPPER_CFG.replace(
            prim_path="{ENV_REGEX_NS}/Robot"
        )

        # Add actions for both the arm and gripper
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=["joint[1-7]"],
            scale=0.5,
            use_default_offset=True,
        )
        self.actions.gripper_action = mdp.BinaryJointPositionActionCfg(
            asset_name="robot",
            joint_names=["finger_joint"],
            open_command_expr={"finger_joint": 0.04},  # Open gripper
            close_command_expr={"finger_joint": 0.0},  # Close gripper
        )

        # Configure the object to lift (cube)
        self.scene.object = RigidObjectCfg(
            prim_path="{ENV_REGEX_NS}/Object",
            spawn=UsdFileCfg(
                usd_path="{NUCLEUS_SERVER}/Isaac/Props/Cube/cube.usd",
                scale=(0.1, 0.1, 0.1),
                rigid_props=RigidBodyPropertiesCfg(
                    disable_gravity=False,
                    solver_position_iteration_count=16,
                    solver_velocity_iteration_count=4,
                ),
            ),
            init_state=RigidObjectCfg.InitialStateCfg(
                pos=[0.5, 0.0, 0.1],
            ),
        )

@configclass
class FlexivCubeLiftEnvCfgPlay(FlexivCubeLiftEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 10  # Use fewer environments for play
        self.scene.env_spacing = 2.5